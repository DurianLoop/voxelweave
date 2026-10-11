"""Inspect the public MSValid ZIP central directory via HTTP byte ranges."""
from __future__ import annotations

import io
import http.client
import json
import time
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path


URL = "https://zenodo.org/api/records/10875606/files/MSValid.zip/content"
SIZE = 2909364362
OUT = Path(__file__).with_name("msvalid_remote_inventory.json")
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class RemoteZip(io.RawIOBase):
    def __init__(self) -> None:
        self.position = 0
        self.transferred = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        self.position = (offset if whence == io.SEEK_SET else
                         self.position + offset if whence == io.SEEK_CUR else SIZE + offset)
        if not 0 <= self.position <= SIZE:
            raise ValueError("ZIP seek outside archive")
        return self.position

    def read(self, length: int = -1) -> bytes:
        length = min(SIZE-self.position, SIZE if length < 0 else length)
        if length <= 0:
            return b""
        start, end = self.position, self.position + length - 1
        request = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}"})
        for attempt in range(3):
            try:
                with OPENER.open(request, timeout=30) as response:
                    if response.status != 206 or response.headers.get("Content-Range") != f"bytes {start}-{end}/{SIZE}":
                        raise IOError("Server did not honor exact ZIP byte range")
                    data = response.read()
                break
            except (OSError, IOError, http.client.HTTPException):
                if attempt == 2:
                    raise
                time.sleep(0.5 * (attempt + 1))
        if len(data) != length:
            raise IOError("Incomplete ZIP byte range")
        self.position += len(data)
        self.transferred += len(data)
        return data


def main() -> None:
    remote = RemoteZip()
    with zipfile.ZipFile(remote) as archive:
        members = archive.infolist()
        result = {
            "source": URL,
            "zenodo_record": "https://zenodo.org/records/10875606",
            "source_archive_bytes": SIZE,
            "metadata_only_bytes_transferred": remote.transferred,
            "files": len([member for member in members if not member.is_dir()]),
            "extensions": dict(Counter(Path(member.filename).suffix.lower()
                                       for member in members if not member.is_dir())),
            "members": [{"path": member.filename,
                         "compressed_bytes": member.compress_size,
                         "uncompressed_bytes": member.file_size,
                         "crc32": f"{member.CRC:08x}"}
                        for member in members if not member.is_dir()],
        }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "members"},
                     ensure_ascii=False, indent=2))
    print("first_members", json.dumps(result["members"][:30], ensure_ascii=False))


if __name__ == "__main__":
    main()
