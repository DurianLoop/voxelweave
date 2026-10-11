"""Download authenticated matched official packages; never run an installer."""
from __future__ import annotations

import hashlib
import json
import shutil
import time
import urllib.request
from pathlib import Path

from probe_vs_seg_original_mask_routes import OUT, ROOT

STAGE = ROOT / "tools/vs_seg_slicer_cpu"


def digest(path, kind="sha512"):
    h = hashlib.new(kind)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    STAGE.mkdir(parents=True, exist_ok=True)
    attempt = len(list(STAGE.glob("download_attempt_*.json"))) + 1
    report = {"attempt": attempt, "script_sha256": digest(Path(__file__), "sha256"), "installer_executed": False, "packages": [], "complete": False}
    start = time.monotonic()
    try:
        free = shutil.disk_usage(ROOT).free
        if free < 15_000_000_000 + 3_000_000_000 + 750_000_000:
            raise OSError("Reserved unpacking space would breach 15 GB floor")
        report["free_before_bytes"] = free
        metadata = [json.loads((OUT / name).read_text())[0] for name in ("slicer_win_stable_files.json", "slicerrt_win_34645_files.json")]
        extension = json.loads((OUT / "slicerrt_win_34645_basename.json").read_text())[0]
        item = json.loads((OUT / "slicer_win_stable_item.json").read_text())
        if str(item["meta"]["revision"]) != str(extension["meta"]["app_revision"]) or not "3b6ce695".startswith(extension["meta"]["revision"]):
            raise ValueError("Matching runtime revision validation failed")
        if extension["meta"]["sha512"] != metadata[1]["sha512"]:
            raise ValueError("Extension item and file digest differ")
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for row in metadata:
            if row["size"] > 750_000_000 or Path(row["name"]).name != row["name"]:
                raise ValueError("Package bound/path failed")
            target = STAGE / row["name"]
            rec = {"file": row["name"], "url": "https://slicer-packages.kitware.com/api/v1/file/" + row["_id"] + "/download", "official_size": row["size"], "official_sha512": row["sha512"]}
            report["packages"].append(rec)
            if not target.exists():
                partial = target.with_suffix(target.suffix + ".partial")
                req = urllib.request.Request(rec["url"], headers={"User-Agent": "MRI-source-audit/1.0"})
                written = 0
                with opener.open(req, timeout=45) as response, partial.open("wb") as stream:
                    rec["final_url"] = response.url
                    while True:
                        chunk = response.read(1_048_576)
                        if not chunk:
                            break
                        written += len(chunk)
                        if written > row["size"]:
                            raise ValueError("Download exceeds official size")
                        stream.write(chunk)
                if written != row["size"] or digest(partial) != row["sha512"]:
                    raise ValueError("Downloaded package authentication failed")
                partial.replace(target)
            if target.stat().st_size != row["size"] or digest(target) != row["sha512"]:
                raise ValueError("Cached official package differs")
            rec.update({"bytes": target.stat().st_size, "sha512_verified": True, "sha256": digest(target, "sha256")})
            print(json.dumps(rec), flush=True)
        report["complete"] = True
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["elapsed_seconds"] = time.monotonic() - start
    report["free_after_bytes"] = shutil.disk_usage(ROOT).free
    (STAGE / f"download_attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attempt": attempt, "complete": report["complete"], "error": report.get("error"), "elapsed_seconds": report["elapsed_seconds"]}), flush=True)
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
