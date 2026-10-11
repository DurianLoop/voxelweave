"""Probe official two-file partial transfer support without starting a transfer."""

from __future__ import annotations

import base64
import hashlib
import http.cookiejar
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from list_upenn_public_package_root import BASE, CLIENT_ID, REDIRECT_URI, Links, NoRedirect, post_json


ROOT = Path(__file__).resolve().parent
OFFICIAL = ROOT / "source_cache" / "upenn_gbm_collection_page_2026-10-01.html"
TREE7 = ROOT / "source_cache" / "upenn_gbm_public_package_tree_v7_2026-10-01.json"
INVENTORY = ROOT / "source_cache" / "upenn_gbm_public_package_inventory_2026-10-01.json"
OUT = ROOT / "source_cache" / "upenn_gbm_partial_transfer_probe_v4_2026-10-01.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    public_url = next(u for u in page.hrefs if u.startswith(BASE + "/aspera/faspex/public/package?"))
    context = urllib.parse.parse_qs(urllib.parse.urlsplit(public_url).query)["context"][0]
    details = json.loads(base64.b64decode(context).decode())
    if details.get("type") != "external_download_package" or details.get("id") != "604":
        raise ValueError("Unexpected public package")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    scan = inventory["preselected_header_pilot_scan"]
    tree7 = json.loads(TREE7.read_text(encoding="utf-8"))
    files = tree7["listings"][2]["entries"]
    t2 = [item for item in files if item["path"].endswith(f"/{scan}_T2.nii.gz")]
    if len(t2) != 1:
        raise ValueError("No unique preselected T2")
    selected = [{"path": t2[0]["path"]}, {"path": inventory["preselected_manual_path"]}]
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar), NoRedirect())
    auth_url = BASE + "/aspera/faspex/auth/authorize_public_link?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI, "state": context,
    })
    try:
        opener.open(urllib.request.Request(auth_url, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=35)
        raise RuntimeError("Expected public-link redirect")
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise
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
        raise RuntimeError(f"Public-link token exchange HTTP {status}")
    body = json.loads(raw)
    token = body.get("data", body).get("access_token")
    if not token:
        raise ValueError("Public-link exchange had no access token")
    endpoint = BASE + "/aspera/faspex/api/v5/packages/604/transfer_spec/download?transfer_type=http_gateway&type=received"
    result_status, result_raw = post_json(opener, endpoint, {"paths": selected}, token)
    report = {
        "package_id": "604", "scan": scan,
        "selected_paths": [item["path"] for item in selected],
        "declared_t2_size": t2[0]["size"],
        "declared_manual_size": inventory["preselected_manual_declared_size"],
        "transfer_spec_http_status": result_status,
        "response_bytes": len(result_raw),
        "response_sha256": hashlib.sha256(result_raw).hexdigest(),
        "transfer_started": False, "patient_pixels_read": False,
        "token_or_spec_archived": False,
    }
    try:
        parsed = json.loads(result_raw)
        report["response_keys"] = sorted(parsed)
        if result_status in (200, 201):
            data = parsed.get("data", parsed)
            report["data_keys"] = sorted(data) if isinstance(data, dict) else []
            spec = data.get("transfer_spec", data) if isinstance(data, dict) else {}
            report["spec_keys"] = sorted(spec) if isinstance(spec, dict) else []
            if isinstance(spec, dict):
                report["spec_source_root"] = spec.get("source_root")
                report["spec_path_fields"] = [
                    {key: value for key, value in path.items() if key in ("source", "destination")}
                    for path in spec.get("paths", []) if isinstance(path, dict)
                ]
                report["spec_ssh_port"] = spec.get("ssh_port")
                report["spec_fasp_port"] = spec.get("fasp_port")
                report["spec_zip_required"] = spec.get("zip_required")
                report["spec_cookie_present"] = bool(spec.get("cookie"))
        else:
            report["error_code"] = parsed.get("code")
            report["error_message"] = str(parsed.get("message", ""))[:300]
    except ValueError:
        report["response_is_json"] = False
    config_request = urllib.request.Request(
        BASE + "/aspera/faspex/api/v5/configuration",
        headers={"Authorization": token, "Accept": "application/json",
                 "User-Agent": "MRI-source-audit/1.0"},
    )
    try:
        with opener.open(config_request, timeout=30) as response:
            config_status, config_raw = response.status, response.read(200_001)
    except urllib.error.HTTPError as error:
        config_status, config_raw = error.code, error.read(1000)
    report["configuration_http_status"] = config_status
    report["configuration_response_sha256"] = hashlib.sha256(config_raw).hexdigest()
    if config_status == 200:
        configuration = json.loads(config_raw)
        config_data = configuration.get("data", configuration)
        if isinstance(config_data, dict):
            report["configuration_keys"] = sorted(config_data)
            gateway = config_data.get("http_gateway_url")
            report["http_gateway_configured"] = isinstance(gateway, str) and bool(gateway)
            if isinstance(gateway, str) and gateway:
                report["http_gateway_hostname"] = urllib.parse.urlsplit(gateway).hostname
            report["prefer_http_connect"] = config_data.get("prefer_http_connect")
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
