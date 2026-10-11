"""Bounded HTTP-range ZIP/gzip prefix audit: decode only NIfTI header bytes."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import math
import struct
import sys
import threading
import urllib.request
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'literature/source_cache/mslesseg_public_zip_metadata_2026-10-02/attempt_01.json'
PLAN = ROOT/'MSLESSEG_SCAN_METADATA_AND_HEADER_PLAN_2026-10-02.md'
OUT = ROOT/'literature/source_cache/mslesseg_raw_t2_headers_2026-10-02'
URL = 'https://ndownloader.figshare.com/files/53623946'
SIZE = 1295472528
BUDGET = 16*1024*1024

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def header_only(compressed):
    outer = zlib.decompressobj(-15)
    gzip_prefix = outer.decompress(compressed, 65536)
    inner = zlib.decompressobj(31)
    first = inner.decompress(gzip_prefix, 4)
    if len(first) < 4:
        return None
    size_le, size_be = struct.unpack('<i', first)[0], struct.unpack('>i', first)[0]
    header_size = size_le if size_le in (348, 540) else size_be
    if header_size not in (348, 540):
        raise ValueError('Unknown NIfTI header size')
    rest = inner.decompress(inner.unconsumed_tail, header_size-4)
    if len(rest) != header_size-4:
        return None
    return first+rest

def parse_header(raw):
    endian = '<' if struct.unpack_from('<i', raw, 0)[0] == len(raw) else '>'
    if len(raw) == 348:
        if raw[344:348] not in (b'n+1\0', b'ni1\0'):
            raise ValueError('Invalid NIfTI-1 magic')
        dim = struct.unpack_from(endian+'8h', raw, 40)
        pixdim = struct.unpack_from(endian+'8f', raw, 76)
        vox_offset = struct.unpack_from(endian+'f', raw, 108)[0]
        units = raw[123]
        qform, sform = struct.unpack_from(endian+'2h', raw, 252)
        srow = [list(struct.unpack_from(endian+'4f', raw, 280+16*i)) for i in range(3)]
        description = raw[148:228].split(b'\0', 1)[0].decode('utf-8', errors='replace')
    else:
        if raw[4:8] not in (b'n+2\0', b'ni2\0'):
            raise ValueError('Invalid NIfTI-2 magic')
        dim = struct.unpack_from(endian+'8q', raw, 16)
        pixdim = struct.unpack_from(endian+'8d', raw, 104)
        vox_offset = struct.unpack_from(endian+'q', raw, 168)[0]
        units = struct.unpack_from(endian+'i', raw, 500)[0]
        qform, sform = struct.unpack_from(endian+'2i', raw, 344)
        srow = [list(struct.unpack_from(endian+'4d', raw, 400+32*i)) for i in range(3)]
        description = raw[240:320].split(b'\0', 1)[0].decode('utf-8', errors='replace')
    if not 3 <= dim[0] <= 7 or any(d <= 0 for d in dim[1:4]):
        raise ValueError('Invalid spatial dimensions')
    if any(not math.isfinite(x) or x <= 0 for x in pixdim[1:4]):
        raise ValueError('Invalid spatial pixdim')
    spatial_units = units & 7
    factor = {1:1000.0, 2:1.0, 3:.001}.get(spatial_units)
    spacing = [float(x)*factor for x in pixdim[1:4]] if factor is not None else None
    norms = [math.sqrt(sum(srow[r][c]**2 for r in range(3)))*factor for c in range(3)] if sform > 0 and factor is not None else None
    return {'nifti_version': 1 if len(raw) == 348 else 2, 'endianness': endian, 'shape': list(dim[1:1+dim[0]]),
            'pixdim': list(pixdim), 'spatial_unit_code': spatial_units, 'spacing_mm': spacing, 'vox_offset': vox_offset,
            'qform_code': qform, 'sform_code': sform, 'srow': srow, 'sform_axis_norms_mm': norms, 'description': description,
            'thin_grid_candidate_le_1_5mm': bool(spacing and max(spacing) <= 1.5),
            'native_thin_acquisition_certified': False, 'raw_label_mapping_certified': False}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob('attempt_*.json')))+1
    source = json.loads(SOURCE.read_text(encoding='utf-8'))
    record = next(r for r in source['records'] if r['key'] == 'raw')
    members = sorted([m for m in record['members'] if m['path'].endswith('_T2.nii.gz')], key=lambda m:m['path'])
    if len(members) != 117 or record['archive_bytes'] != SIZE or any(m['compression_method'] != 8 for m in members):
        raise ValueError('Frozen raw T2 directory differs')
    selection = {'inventory_sha256': sha(SOURCE), 'plan_sha256': sha(PLAN), 'script_sha256': sha(__file__), 'members': members}
    selection_path = OUT/f'selection_attempt_{attempt:02d}.json'
    selection_path.write_text(json.dumps(selection, indent=2)+'\n', encoding='utf-8')
    ledger, reserved = [], [0]
    lock = threading.Lock()
    def get_range(index, label, start, length):
        if length <= 0 or length > 65536 or start < 0 or start+length > SIZE:
            raise ValueError('Invalid bounded range')
        entry = {'member_index': index, 'label': label, 'start': start, 'end': start+length-1, 'requested_bytes': length}
        with lock:
            if reserved[0]+length > BUDGET:
                raise ValueError('Total request budget exceeded')
            reserved[0] += length
            ledger.append(entry)
        req = urllib.request.Request(URL, headers={'User-Agent':'MRI-public-header-audit/1.0',
                                                  'Range':f'bytes={start}-{start+length-1}', 'Accept-Encoding':'identity'})
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=30) as response:
                entry.update(http_status=response.status, content_range=response.headers.get('Content-Range'), final_url=response.url)
                if response.status != 206 or entry['content_range'] != f'bytes {start}-{start+length-1}/{SIZE}':
                    raise ValueError('Exact HTTP range not honored')
                raw = response.read(length+1)
            if len(raw) != length:
                raise ValueError('Range body length differs')
            path = OUT/f'raw_{index:03d}_{label}_attempt_{attempt:02d}.bin'
            path.write_bytes(raw)
            entry.update(file=path.name, bytes=len(raw), sha256=sha(path))
            return raw
        except Exception as exc:
            entry['error'] = f'{type(exc).__name__}: {exc}'
            raise
    def one(index, member):
        result = {'member_index': index, 'path': member['path'], 'central_directory': member, 'header_complete': False}
        try:
            offset = member['header_offset']
            local = get_range(index, 'lfh', offset, 30)
            fields = struct.unpack('<4s5H3I2H', local)
            if fields[0] != b'PK\x03\x04' or fields[3] != 8 or fields[2]&1:
                raise ValueError('Unexpected ZIP local signature/compression/encryption')
            name_length, extra_length = fields[-2:]
            if name_length+extra_length > 16384:
                raise ValueError('ZIP name/extra exceeds cap')
            name_extra = get_range(index, 'name_extra', offset+30, name_length+extra_length)
            name = name_extra[:name_length].decode('utf-8' if fields[2]&2048 else 'cp437')
            if name != member['path']:
                raise ValueError('Local member name differs from central directory')
            data_start = offset+30+name_length+extra_length
            result['data_start'] = data_start
            for cap in (8192, 32768, 65536):
                prefix = get_range(index, f'prefix{cap}', data_start, min(cap, member['compressed_bytes']))
                header = header_only(prefix)
                if header is not None:
                    path = OUT/f'raw_{index:03d}_nifti_header_attempt_{attempt:02d}.bin'
                    path.write_bytes(header)
                    result.update(header_complete=True, header_file=path.name, header_bytes=len(header), header_sha256=sha(path),
                                  decoded=parse_header(header), member_full_crc_verified=False, gzip_trailer_verified=False)
                    break
                if cap >= member['compressed_bytes']:
                    break
            if not result['header_complete']:
                raise ValueError('Header unavailable within prefix budget')
        except Exception as exc:
            result['error'] = f'{type(exc).__name__}: {exc}'
        print(json.dumps({k:result.get(k) for k in ('member_index','path','header_complete','error')}, ensure_ascii=False), flush=True)
        return result
    started = datetime.now(timezone.utc).isoformat()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(one, i, m) for i, m in enumerate(members)]
        results = [f.result() for f in futures]
    output = {'attempt': attempt, 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'script_sha256': sha(__file__), 'plan_sha256': sha(PLAN), 'selection_file': selection_path.name,
              'selection_sha256': sha(selection_path), 'records': results, 'requests': ledger,
              'requested_range_bytes': reserved[0], 'transferred_range_bytes': sum(r.get('bytes',0) for r in ledger),
              'complete_headers': sum(r['header_complete'] for r in results),
              'thin_grid_candidates': sum(r.get('decoded',{}).get('thin_grid_candidate_le_1_5mm', False) for r in results),
              'native_thin_acquisition_certified': 0, 'patient_pixels_decoded': False, 'full_archive_downloaded': False,
              'errors': [r['path']+': '+r['error'] for r in results if 'error' in r]}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in output.items() if k not in ('records','requests')}, ensure_ascii=False), flush=True)
    return int(bool(output['errors']))

if __name__ == '__main__':
    raise SystemExit(main())
