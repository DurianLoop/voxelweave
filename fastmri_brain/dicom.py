from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct

import numpy as np


IMPLICIT_LE = "1.2.840.10008.1.2"
EXPLICIT_LE = "1.2.840.10008.1.2.1"
EXPLICIT_BE = "1.2.840.10008.1.2.2"


@dataclass(frozen=True)
class DicomSlice:
    path: Path
    instance_number: int
    rows: int
    cols: int
    pixel_spacing: tuple[float, float] | None
    slice_thickness: float | None
    spacing_between_slices: float | None
    image_position: tuple[float, float, float] | None
    transfer_syntax: str


def _clean_text(value: bytes) -> str:
    return value.decode("latin-1", errors="ignore").strip().strip("\x00")


def _numbers(value: bytes) -> list[float]:
    text = _clean_text(value)
    if not text:
        return []
    out = []
    for item in text.split("\\"):
        try:
            out.append(float(item.strip()))
        except ValueError:
            pass
    return out


def _read_us(value: bytes, endian: str = "<") -> int:
    if len(value) < 2:
        return 0
    return int(struct.unpack(endian + "H", value[:2])[0])


def _read_is(value: bytes) -> int:
    text = _clean_text(value)
    try:
        return int(float(text))
    except ValueError:
        return 0


def _find_implicit_value(data: bytes, group: int, elem: int, last: bool = False) -> bytes | None:
    marker = struct.pack("<HH", group, elem)
    pos = data.rfind(marker) if last else data.find(marker)
    if pos < 0 or pos + 8 > len(data):
        return None
    length = struct.unpack("<I", data[pos + 4 : pos + 8])[0]
    if length == 0xFFFFFFFF or pos + 8 + length > len(data):
        return None
    return data[pos + 8 : pos + 8 + length]


def _find_text_numbers(data: bytes, group: int, elem: int) -> list[float]:
    value = _find_implicit_value(data, group, elem)
    return [] if value is None else _numbers(value)


def _parse_meta(data: bytes) -> tuple[str, int]:
    offset = 132 if data[128:132] == b"DICM" else 0
    transfer = IMPLICIT_LE
    while offset + 8 <= len(data):
        group, elem = struct.unpack("<HH", data[offset : offset + 4])
        if group != 0x0002:
            break
        vr = data[offset + 4 : offset + 6].decode("ascii", errors="ignore")
        if vr in {"OB", "OW", "OF", "SQ", "UT", "UN"}:
            length = struct.unpack("<I", data[offset + 8 : offset + 12])[0]
            value_start = offset + 12
        else:
            length = struct.unpack("<H", data[offset + 6 : offset + 8])[0]
            value_start = offset + 8
        value = data[value_start : value_start + length]
        if (group, elem) == (0x0002, 0x0010):
            transfer = _clean_text(value)
        offset = value_start + length
    return transfer, offset


def _iter_elements(data: bytes, offset: int, transfer_syntax: str):
    if transfer_syntax == EXPLICIT_BE:
        endian = ">"
    else:
        endian = "<"
    explicit = transfer_syntax in {EXPLICIT_LE, EXPLICIT_BE}
    while offset + 8 <= len(data):
        group, elem = struct.unpack(endian + "HH", data[offset : offset + 4])
        if explicit:
            vr = data[offset + 4 : offset + 6].decode("ascii", errors="ignore")
            if vr in {"OB", "OW", "OF", "SQ", "UT", "UN"}:
                if offset + 12 > len(data):
                    break
                length = struct.unpack(endian + "I", data[offset + 8 : offset + 12])[0]
                value_start = offset + 12
            else:
                length = struct.unpack(endian + "H", data[offset + 6 : offset + 8])[0]
                value_start = offset + 8
        else:
            length = struct.unpack(endian + "I", data[offset + 4 : offset + 8])[0]
            value_start = offset + 8
        if length == 0xFFFFFFFF:
            break
        value_end = value_start + length
        if value_end > len(data):
            break
        yield (group, elem), data[value_start:value_end], endian
        offset = value_end


def read_header(path: Path) -> DicomSlice:
    data = Path(path).read_bytes()
    transfer, offset = _parse_meta(data)
    fields: dict[tuple[int, int], bytes] = {}
    for tag, value, _endian in _iter_elements(data, offset, transfer):
        fields[tag] = value
        if tag == (0x7FE0, 0x0010):
            break
    rows_value = fields.get((0x0028, 0x0010)) or _find_implicit_value(data, 0x0028, 0x0010) or b""
    cols_value = fields.get((0x0028, 0x0011)) or _find_implicit_value(data, 0x0028, 0x0011) or b""
    rows = _read_us(rows_value)
    cols = _read_us(cols_value)
    spacing_values = _numbers(fields.get((0x0028, 0x0030), b"")) or _find_text_numbers(data, 0x0028, 0x0030)
    position_values = _numbers(fields.get((0x0020, 0x0032), b"")) or _find_text_numbers(data, 0x0020, 0x0032)
    thickness_values = _numbers(fields.get((0x0018, 0x0050), b"")) or _find_text_numbers(data, 0x0018, 0x0050)
    spacing_between_values = _numbers(fields.get((0x0018, 0x0088), b"")) or _find_text_numbers(data, 0x0018, 0x0088)
    instance_number = _read_is(fields.get((0x0020, 0x0013), b"0"))
    if instance_number == 0:
        value = _find_implicit_value(data, 0x0020, 0x0013)
        instance_number = _read_is(value or b"0")
    if instance_number == 0:
        try:
            instance_number = int(Path(path).stem)
        except ValueError:
            instance_number = 0
    return DicomSlice(
        path=Path(path),
        instance_number=instance_number,
        rows=rows,
        cols=cols,
        pixel_spacing=(spacing_values[0], spacing_values[1]) if len(spacing_values) >= 2 else None,
        slice_thickness=thickness_values[0] if thickness_values else None,
        spacing_between_slices=spacing_between_values[0] if spacing_between_values else None,
        image_position=(position_values[0], position_values[1], position_values[2])
        if len(position_values) >= 3
        else None,
        transfer_syntax=transfer,
    )


def read_pixel_array(path: Path) -> np.ndarray:
    data = Path(path).read_bytes()
    transfer, offset = _parse_meta(data)
    if transfer not in {IMPLICIT_LE, EXPLICIT_LE}:
        raise ValueError(f"Unsupported transfer syntax {transfer} for {path}")
    rows = cols = bits_allocated = pixel_repr = 0
    slope = 1.0
    intercept = 0.0
    pixel_data: bytes | None = None
    for tag, value, endian in _iter_elements(data, offset, transfer):
        if tag == (0x0028, 0x0010):
            rows = _read_us(value, endian)
        elif tag == (0x0028, 0x0011):
            cols = _read_us(value, endian)
        elif tag == (0x0028, 0x0100):
            bits_allocated = _read_us(value, endian)
        elif tag == (0x0028, 0x0103):
            pixel_repr = _read_us(value, endian)
        elif tag == (0x0028, 0x1052):
            nums = _numbers(value)
            intercept = nums[0] if nums else 0.0
        elif tag == (0x0028, 0x1053):
            nums = _numbers(value)
            slope = nums[0] if nums else 1.0
        elif tag == (0x7FE0, 0x0010):
            pixel_data = value
            break
    if not rows:
        value = _find_implicit_value(data, 0x0028, 0x0010)
        rows = _read_us(value or b"")
    if not cols:
        value = _find_implicit_value(data, 0x0028, 0x0011)
        cols = _read_us(value or b"")
    if not bits_allocated:
        value = _find_implicit_value(data, 0x0028, 0x0100)
        bits_allocated = _read_us(value or b"")
    if pixel_repr == 0:
        value = _find_implicit_value(data, 0x0028, 0x0103)
        pixel_repr = _read_us(value or b"")
    if pixel_data is None:
        pixel_data = _find_implicit_value(data, 0x7FE0, 0x0010, last=True)
    if not rows or not cols or pixel_data is None:
        raise ValueError(f"Could not read pixel data from {path}")
    if bits_allocated == 16:
        dtype = np.int16 if pixel_repr else np.uint16
    elif bits_allocated == 8:
        dtype = np.int8 if pixel_repr else np.uint8
    else:
        raise ValueError(f"Unsupported BitsAllocated={bits_allocated} for {path}")
    expected = rows * cols * np.dtype(dtype).itemsize
    arr = np.frombuffer(pixel_data[:expected], dtype=dtype).reshape(rows, cols).astype(np.float32)
    return arr * float(slope) + float(intercept)


def load_case_volume(case_dir: Path) -> tuple[np.ndarray, list[DicomSlice]]:
    paths = sorted(Path(case_dir).glob("*.dcm"))
    headers = [read_header(path) for path in paths]
    headers = sorted(headers, key=lambda item: item.instance_number)
    volume = np.stack([read_pixel_array(item.path) for item in headers], axis=-1).astype(np.float32)
    return volume, headers
