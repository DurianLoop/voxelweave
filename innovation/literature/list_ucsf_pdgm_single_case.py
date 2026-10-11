"""List the preselected UCSF-PDGM-005 NIfTI directory without file transfer."""

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


HERE = Path(__file__).resolve().parent
OFFICIAL = HERE / "source_cache" / "ucsf_pdgm_official_2026-10-01" / "page.html"
ROOT_LIST = HERE / "source_cache" / "ucsf_pdgm_public_package_metadata_2026-10-01.json"
OUT = HERE / "source_cache" / "ucsf_pdgm_005_file_list_2026-10-01.json"
CASE = "UCSF-PDGM-005"
DIR = "/UCSF-PDGM-v5/UCSF-PDGM-0005_nifti"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    root = json.loads(ROOT_LIST.read_text(encoding="utf-8"))
    matches = [entry for entry in root["listings"][1]["entries"] if entry.get("path") == DIR]
    if len(matches) != 1 or matches[0].get("type") != "directory":
        raise ValueError("Frozen case directory missing from official root listing")
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    contexts = []
    for link in page.hrefs:
        if not link.startswith(BASE + "/aspera/faspex?"):
            continue
        context = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query).get("context", [None])[0]
        if context and json.loads(base64.b64decode(context).decode()).get("id") == "1065":
            contexts.append(context)
    if len(contexts) != 1:
        raise ValueError("Unexpected official public package link count")
    context = contexts[0]
    report = {"case_csv_id": CASE, "package_id": "1065", "directory": DIR,
              "root_listing_sha256": hashlib.sha256(ROOT_LIST.read_bytes()).hexdigest(),
              "transfer_started": False, "patient_pixels_read": False}
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect()
    )
    try:
        authorize = BASE + "/aspera/faspex/auth/authorize_public_link?" + urllib.parse.urlencode({
            "response_type": "code", "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI, "state": context,
        })
        try:
            opener.open(urllib.request.Request(authorize, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=35)
            raise RuntimeError("Expected authorization redirect")
        except urllib.error.HTTPError as error:
            report["auth_http_status"] = error.code
            redirect = urllib.parse.urlsplit(error.headers.get("Location", ""))
        if report["auth_http_status"] != 302 or redirect.path != "/aspera/faspex/token":
            raise RuntimeError("Unexpected public authorization response")
        args = urllib.parse.parse_qs(redirect.query)
        status, raw = post_json(opener, BASE + "/aspera/faspex/auth/token", {
            "code": args["code"][0], "state": args.get("state", [""])[0],
            "grant_type": "authorization_code", "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
        })
        report["token_http_status"] = status
        if status not in (200, 201):
            raise RuntimeError("Public token exchange failed")
        body = json.loads(raw)
        token = body.get("data", body).get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Missing public session")
        endpoint = BASE + "/aspera/faspex/api/v5/packages/1065/files/received/page?offset=0&limit=1000"
        status, raw = post_json(opener, endpoint, {"path": DIR}, token)
        report["http_status"] = status
        report["response_bytes"] = len(raw)
        report["response_sha256"] = hashlib.sha256(raw).hexdigest()
        if status == 200:
            listing = json.loads(raw)
            data = listing.get("data", listing)
            entries = data.get("items", [])
            report["item_count"] = data.get("item_count")
            report["entries_returned"] = len(entries)
            report["entries"] = [
                {key: entry.get(key) for key in ("name", "path", "type", "size", "is_dir") if key in entry}
                for entry in entries[:1000]
            ]
            report["truncated_by_limit"] = len(entries) >= 1000
    except (KeyError, ValueError, RuntimeError, urllib.error.URLError, TimeoutError) as error:
        report["error_type"] = type(error).__name__
        report["error_stage"] = "public_auth_or_listing"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
