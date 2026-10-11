"""One bounded official-ascli transfer of the preselected UCSF T2/label pair."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.parse
from pathlib import Path

from list_upenn_public_package_root import BASE, Links


HERE = Path(__file__).resolve().parent
INNOVATION = HERE.parent
OFFICIAL = HERE / "source_cache" / "ucsf_pdgm_official_2026-10-01" / "page.html"
SPEC = HERE / "source_cache" / "ucsf_two_file_transfer_spec_probe_2026-10-01.json"
CLI = INNOVATION / "tools" / "aspera_cli_4.27.3" / "extracted" / "ascli.cmd"
FETCH = INNOVATION / "tools" / "aspera_cli_4.27.3" / "fetch_report.json"
DEST = INNOVATION / "data" / "ucsf_pdgm_005_header_pilot_v2_2026-10-01"
HOME = INNOVATION / "data" / "ucsf_pdgm_005_ascli_home_v2_2026-10-01"
OUT = HERE / "source_cache" / "ucsf_two_file_ascli_pilot_v2_2026-10-01.json"
SOURCES = HERE / "source_cache" / "ucsf_ascli_exact_sources_2026-10-01.txt"
MAX_BYTES = 10_000_000
TIMEOUT_SEC = 120


def public_link() -> str:
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    matches = []
    for link in page.hrefs:
        if not link.startswith(BASE + "/aspera/faspex?"):
            continue
        context = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query).get("context", [None])[0]
        if context and json.loads(base64.b64decode(context).decode()).get("id") == "1065":
            matches.append(link)
    if len(matches) != 1:
        raise ValueError("Unexpected official public link count")
    return matches[0]


def terminate_own_tree(pid: int) -> bool:
    result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            timeout=10, check=False)
    return result.returncode == 0


def total_file_bytes(folder: Path) -> int:
    return sum(path.stat().st_size for path in folder.rglob("*") if path.is_file())


def main() -> None:
    if OUT.exists() or DEST.exists() or HOME.exists():
        raise FileExistsError("Pilot output or destination already exists; refusing repeat")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    expected = (
        "/UCSF-PDGM-v5/UCSF-PDGM-0005_nifti/UCSF-PDGM-0005_T2.nii.gz",
        "/UCSF-PDGM-v5/UCSF-PDGM-0005_nifti/UCSF-PDGM-0005_tumor_segmentation.nii.gz",
    )
    if not spec.get("spec_scope_pass") or tuple(spec["requested_paths"]) != expected:
        raise ValueError("Preflight spec scope did not pass exact two-file check")
    if tuple(SOURCES.read_text(encoding="utf-8").splitlines()) != expected:
        raise ValueError("Explicit ascli source file differs from frozen paths")
    if sum(spec["declared_bytes"]) != 2_744_058:
        raise ValueError("Official declared byte count changed")
    fetch = json.loads(FETCH.read_text(encoding="utf-8"))
    if fetch["sha256"] != "64c58a092fa7609ffeb8a212cc8bbd70fb0147d4498d3c909909c8dca29b01fd":
        raise ValueError("Official CLI digest record changed")
    if not CLI.is_file():
        raise FileNotFoundError(CLI)
    link = public_link()
    report = {
        "tool": "IBM ascli 4.27.3 Windows portable", "package_id": "1065",
        "requested_paths": list(expected), "declared_bytes": spec["declared_bytes"],
        "preflight_spec_report_sha256": hashlib.sha256(SPEC.read_bytes()).hexdigest(),
        "public_link_sha256": hashlib.sha256(link.encode()).hexdigest(),
        "max_local_bytes": MAX_BYTES, "deadline_seconds": TIMEOUT_SEC,
        "target_rate_kbps": 5000, "credential_or_transfer_spec_archived": False,
        "patient_pixels_decoded": False, "gpu_used": False,
    }
    DEST.mkdir(parents=True)
    HOME.mkdir(parents=True)
    env = os.environ.copy()
    env["TCIA_UCSF_PUBLIC_URL"] = link
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env.pop(name, None)
    env["NO_PROXY"] = "*"
    env["no_proxy"] = "*"
    env["CUDA_VISIBLE_DEVICES"] = "-1"
    command = [str(CLI), "faspex5", "packages", "receive",
               f"--sources=@lines:@file:{SOURCES}",
               "--url=@env:TCIA_UCSF_PUBLIC_URL", f"--home={HOME}",
               f"--to-folder={DEST}", "--ts.target_rate_kbps=5000",
               "--ts.rate_policy=low", "--transfer.resume.iter_max=0",
               "--progress-bar=no", "--format=json"]
    process = subprocess.Popen(command, env=env, cwd=CLI.parent,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    report["transfer_command_started"] = True
    deadline = time.monotonic() + TIMEOUT_SEC
    stop_reason = None
    while process.poll() is None:
        size = total_file_bytes(DEST)
        names = [path.name for path in DEST.rglob("*") if path.is_file()]
        if size > MAX_BYTES:
            stop_reason = "local byte cap exceeded"
        elif any(name not in {Path(path).name for path in expected} for name in names):
            stop_reason = "unexpected output filename"
        elif time.monotonic() > deadline:
            stop_reason = "120-second deadline exceeded"
        if stop_reason:
            report["own_process_tree_terminated"] = terminate_own_tree(process.pid)
            break
        time.sleep(0.2)
    try:
        stdout, stderr = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        report["own_process_tree_terminated"] = terminate_own_tree(process.pid)
        stdout, stderr = process.communicate(timeout=10)
    report["exit_code"] = process.returncode
    report["stop_reason"] = stop_reason
    report["stdout_bytes"] = len(stdout)
    report["stdout_sha256"] = hashlib.sha256(stdout).hexdigest()
    report["stderr_bytes"] = len(stderr)
    report["stderr_sha256"] = hashlib.sha256(stderr).hexdigest()
    safe_errors = []
    for line in stderr.decode("utf-8", "replace").splitlines():
        line = line.replace(link, "[PUBLIC_LINK]")
        line = re.sub(r"https?://\S+", "[URL]", line)
        line = re.sub(r"[A-Za-z0-9_+=/-]{48,}", "[REDACTED]", line)
        if len(line) <= 260 and not any(word in line.lower() for word in
                                        ("cookie", "authorization", "passcode")):
            safe_errors.append(line)
    report["safe_error_lines"] = safe_errors[-10:]
    report["files"] = []
    for path in sorted(DEST.rglob("*")):
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        report["files"].append({"relative_path": path.relative_to(DEST).as_posix(),
                                "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    report["total_local_bytes"] = total_file_bytes(DEST)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if HOME.resolve().is_relative_to((INNOVATION / "data").resolve()):
        shutil.rmtree(HOME)
        report["isolated_home_removed"] = True
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
