"""Read-only official ascli browse of the frozen UCSF case directory."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.parse
from pathlib import Path

from list_upenn_public_package_root import BASE, Links


HERE = Path(__file__).resolve().parent
INNOVATION = HERE.parent
OFFICIAL = HERE / "source_cache" / "ucsf_pdgm_official_2026-10-01" / "page.html"
CLI = INNOVATION / "tools" / "aspera_cli_4.27.3" / "extracted" / "ascli.cmd"
OUT = HERE / "source_cache" / "ibm_ascli_ucsf_browse_v5_2026-10-01.json"
CASE_DIR = "/"
EXPECTED = ("UCSF-PDGM-v5",)


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
        raise ValueError("Expected exactly one official v5 public link")
    return matches[0]


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    if not CLI.is_file():
        raise FileNotFoundError(CLI)
    link = public_link()
    report = {"tool": "IBM ascli 4.27.3", "package_id": "1065", "requested_path": CASE_DIR,
              "public_link_sha256": hashlib.sha256(link.encode()).hexdigest(),
              "transfer_started": False, "patient_pixels_read": False,
              "credentials_archived": False}
    home = INNOVATION / "data" / "ibm_ascli_ucsf_browse_home_v5_2026-10-01"
    home.mkdir(exist_ok=False)
    env = os.environ.copy()
    env["TCIA_UCSF_PUBLIC_URL"] = link
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        env.pop(name, None)
    env["NO_PROXY"] = "*"
    env["no_proxy"] = "*"
    command = [str(CLI), "faspex5", "packages", "browse",
               "--url=@env:TCIA_UCSF_PUBLIC_URL", f"--home={home}",
               "--query.max=30", "--format=json"]
    try:
        result = subprocess.run(command, env=env, cwd=CLI.parent,
                                capture_output=True, timeout=45, check=False)
        report["exit_code"] = result.returncode
        report["stdout_bytes"] = len(result.stdout)
        report["stdout_sha256"] = hashlib.sha256(result.stdout).hexdigest()
        report["stderr_bytes"] = len(result.stderr)
        report["stderr_sha256"] = hashlib.sha256(result.stderr).hexdigest()
        report["expected_names_found"] = {
            name: name.encode() in result.stdout for name in EXPECTED
        }
        report["error_class"] = (
            "authentication" if b"authenticat" in result.stderr.lower() else
            "connection" if b"connect" in result.stderr.lower() else
            "other" if result.returncode else None
        )
        safe_lines = []
        for line in result.stderr.decode("utf-8", "replace").splitlines():
            line = line.replace(link, "[PUBLIC_LINK]")
            line = re.sub(r"https?://\S+", "[URL]", line)
            line = re.sub(r"[A-Za-z0-9_+=/-]{48,}", "[REDACTED]", line)
            if len(line) <= 260 and not any(word in line.lower() for word in
                                            ("cookie", "authorization", "passcode")):
                safe_lines.append(line)
        report["safe_error_lines"] = safe_lines[-8:]
    except subprocess.TimeoutExpired:
        report["error_class"] = "timeout"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if home.resolve().is_relative_to((INNOVATION / "data").resolve()):
        shutil.rmtree(home)
        report["isolated_home_removed"] = True
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
