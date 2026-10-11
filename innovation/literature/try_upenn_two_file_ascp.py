"""Bounded public Faspex pilot for the two preselected UPENN NIfTI files.

Credentials and the transfer spec exist only in memory. The report contains no
raw subprocess output or authorization material.
"""

from __future__ import annotations

import base64
import hashlib
import http.cookiejar
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from list_upenn_public_package_root import BASE, CLIENT_ID, REDIRECT_URI, Links, NoRedirect, post_json


HERE = Path(__file__).resolve().parent
INNOVATION = HERE.parent
OFFICIAL = HERE / "source_cache" / "upenn_gbm_collection_page_2026-10-01.html"
INVENTORY = HERE / "source_cache" / "upenn_gbm_public_package_inventory_2026-10-01.json"
TREE = HERE / "source_cache" / "upenn_gbm_public_package_tree_v7_2026-10-01.json"
PREVIOUS_SPEC = HERE / "source_cache" / "upenn_gbm_partial_transfer_probe_v4_2026-10-01.json"
REPORT = HERE / "source_cache" / "upenn_gbm_two_file_ascp_pilot_v9_2026-10-01.json"
DEST = INNOVATION / "data" / "upenn_gbm_two_file_header_pilot_2026-10-01"
ASCP = INNOVATION / "tools" / "ibm_aspera_connect_4.2.19.956" / "portable" / "ascp.exe"
KEY = ASCP.parent / "aspera_tokenauth_id_rsa"
LICENSE = ASCP.parent / "aspera-license"
LIMIT = 10_000_000


def authorize_and_spec(paths: list[str]) -> dict:
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    public_url = next(u for u in page.hrefs if u.startswith(BASE + "/aspera/faspex/public/package?"))
    context = urllib.parse.parse_qs(urllib.parse.urlsplit(public_url).query)["context"][0]
    details = json.loads(base64.b64decode(context).decode())
    if details.get("type") != "external_download_package" or details.get("id") != "604":
        raise ValueError("Unexpected public package")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect()
    )
    url = BASE + "/aspera/faspex/auth/authorize_public_link?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI, "state": context,
    })
    try:
        opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=35)
        raise RuntimeError("Expected redirect")
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise RuntimeError(f"Authorization HTTP {error.code}") from None
        redirect = urllib.parse.urlsplit(error.headers["Location"])
    if redirect.path != "/aspera/faspex/token":
        raise ValueError("Unexpected auth redirect")
    query = urllib.parse.parse_qs(redirect.query)
    status, raw = post_json(opener, BASE + "/aspera/faspex/auth/token", {
        "code": query["code"][0], "state": query.get("state", [""])[0],
        "grant_type": "authorization_code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    })
    if status not in (200, 201):
        raise RuntimeError(f"Token exchange HTTP {status}")
    body = json.loads(raw)
    bearer = body.get("data", body).get("access_token")
    if not bearer:
        raise ValueError("No public session")
    endpoint = BASE + "/aspera/faspex/api/v5/packages/604/transfer_spec/download?transfer_type=connect&type=received"
    status, raw = post_json(opener, endpoint, {"paths": [{"path": path} for path in paths]}, bearer)
    if status not in (200, 201):
        raise RuntimeError(f"Two-file spec HTTP {status}")
    body = json.loads(raw)
    data = body.get("data", body)
    return data.get("transfer_spec", data)


def main() -> None:
    if REPORT.exists():
        raise FileExistsError("Pilot report exists; refusing repeat")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    scan = inventory["preselected_header_pilot_scan"]
    if scan != "UPENN-GBM-00002_11":
        raise ValueError("Frozen scan changed")
    tree = json.loads(TREE.read_text(encoding="utf-8"))
    t2 = [entry for entry in tree["listings"][2]["entries"]
          if entry["path"].endswith(f"/{scan}_T2.nii.gz")]
    if len(t2) != 1:
        raise ValueError("Expected one exact T2")
    paths = [t2[0]["path"], inventory["preselected_manual_path"]]
    if len(set(paths)) != 2 or any(not p.startswith("/UPENN-GBM/NIfTI-files/") or ".." in p for p in paths):
        raise ValueError("Unsafe source paths")
    report = {"package_id": "604", "scan": scan, "selected_paths": paths,
              "declared_bytes": [t2[0]["size"], inventory["preselected_manual_declared_size"]],
              "max_local_bytes": LIMIT, "transfer_started": False,
              "pixel_data_decoded": False, "secret_or_spec_archived": False}
    stage = "request_spec"
    try:
        spec = authorize_and_spec(paths)
        stage = "validate_paths"
        root = spec.get("source_root")
        host = spec.get("remote_host")
        user = spec.get("remote_user")
        actual = [p.get("source") for p in spec.get("paths", [])]
        known_root = json.loads(PREVIOUS_SPEC.read_text(encoding="utf-8"))["spec_source_root"]
        expected = [known_root + path for path in paths]
        report["spec_path_count"] = len(actual)
        report["paths_equal_expected_full_paths"] = actual == expected
        report["source_root_null"] = root is None
        if actual != expected or root is not None:
            raise ValueError("Transfer spec scope mismatch")
        stage = "validate_host"
        if not isinstance(host, str) or not re.fullmatch(r"[A-Za-z0-9.-]+", host):
            raise ValueError("Invalid transfer host")
        stage = "validate_user"
        if not isinstance(user, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", user):
            raise ValueError("Invalid transfer user")
        stage = "validate_auth_kind"
        report["authentication_kind"] = spec.get("authentication") if spec.get("authentication") in ("token", "password", "publickey") else "other"
        if spec.get("direction") != "receive" or spec.get("authentication") != "token":
            raise ValueError("Unexpected transfer authentication")
        stage = "validate_credentials_present"
        if not spec.get("token") or not spec.get("cookie"):
            raise ValueError("Missing transfer credential")
        stage = "validate_portable_tool"
        if not ASCP.is_file() or not KEY.is_file() or not LICENSE.is_file():
            raise ValueError("Official portable ascp is unavailable")
        report["portable_license_sha256"] = hashlib.sha256(LICENSE.read_bytes()).hexdigest()
        report.update({"spec_path_count": len(actual), "spec_zip_required": spec.get("zip_required"),
                       "spec_ssh_port": spec.get("ssh_port"), "spec_fasp_port": spec.get("fasp_port"),
                       "remote_host": host})
        stage = "validate_empty_destination"
        DEST.mkdir(parents=True, exist_ok=True)
        if any(DEST.iterdir()):
            raise ValueError("Pilot destination is not empty")
        sources = [f"{user}@{host}:{path}" for path in actual]
        command = [str(ASCP), "-q", "-i", str(KEY), "-P", str(int(spec["ssh_port"])),
                   "-O", str(int(spec["fasp_port"])), "-l", "5m",
                   "--mode=recv", "--overwrite=never",
                   *sources, str(DEST)]
        env = os.environ.copy()
        env["ASPERA_SCP_TOKEN"] = spec["token"]
        env["ASPERA_SCP_COOKIE"] = spec["cookie"]
        stage = "launch_ascp"
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env)
        report["transfer_started"] = True
        deadline = time.monotonic() + 120
        stop_reason = None
        while process.poll() is None:
            size = sum(p.stat().st_size for p in DEST.rglob("*") if p.is_file())
            if size > LIMIT:
                stop_reason = "local byte limit exceeded"
            elif time.monotonic() > deadline:
                stop_reason = "120-second timeout"
            if stop_reason:
                process.kill()
                break
            time.sleep(0.2)
        return_code = process.wait(timeout=10)
        error_bytes = process.stderr.read(100_000) if process.stderr else b""
        diagnostic_logs = list(ASCP.parent.glob("aspera-scp-transfer*.log"))
        report["ephemeral_log_count_removed"] = len(diagnostic_logs)
        for log in diagnostic_logs:
            log.unlink()
        lowered = error_bytes.decode("utf-8", "replace").lower()
        report["stderr_bytes"] = len(error_bytes)
        report["stderr_sha256"] = hashlib.sha256(error_bytes).hexdigest()
        if len(error_bytes) <= 200:
            redacted = lowered.replace(spec["token"].lower(), "[secret]").replace(spec["cookie"].lower(), "[secret]")
            report["stderr_redacted"] = redacted
        report["error_markers"] = [name for name, pattern in {
            "authentication": r"auth|permission|token|cookie|denied",
            "network": r"connect|timeout|unreachable|socket|network",
            "source_path": r"not found|no such file|source|symbolic link",
            "cli_syntax": r"invalid|unknown|usage|option|argument",
            "ssh_key": r"key|publickey|host fingerprint",
        }.items() if re.search(pattern, lowered)]
        report["ascp_exit_code"] = return_code
        report["stop_reason"] = stop_reason
        files = sorted(p for p in DEST.rglob("*") if p.is_file())
        report["files"] = [{"relative_path": p.relative_to(DEST).as_posix(),
                            "bytes": p.stat().st_size,
                            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
        report["total_local_bytes"] = sum(item["bytes"] for item in report["files"])
        report["two_exact_files_received"] = (return_code == 0 and not stop_reason and
            sorted(p.name for p in files) == sorted(Path(p).name for p in paths) and
            report["total_local_bytes"] <= LIMIT)
    except Exception as error:
        report["pilot_error_type"] = type(error).__name__
        report["pilot_error_stage"] = stage
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
