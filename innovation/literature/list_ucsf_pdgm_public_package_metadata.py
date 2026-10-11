"""List at most two levels of the official public UCSF Faspex package."""

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
OUT = HERE / "source_cache" / "ucsf_pdgm_public_package_metadata_2026-10-01.json"
PACKAGE_ID = "1065"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    links = [url for url in page.hrefs if url.startswith(BASE + "/aspera/faspex?")]
    candidates = []
    for link in links:
        context = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query).get("context", [None])[0]
        if not context:
            continue
        details = json.loads(base64.b64decode(context).decode("utf-8"))
        if details.get("id") == PACKAGE_ID and details.get("type") == "external_download_package":
            candidates.append((link, context))
    if len(candidates) != 1:
        raise ValueError(f"Expected one official v5 package link; got {len(candidates)}")
    link, context = candidates[0]
    report = {
        "official_link_sha256": hashlib.sha256(link.encode()).hexdigest(),
        "official_page_sha256": hashlib.sha256(OFFICIAL.read_bytes()).hexdigest(),
        "package_id": PACKAGE_ID,
        "package_transfer_started": False,
        "patient_pixels_read": False,
        "listings": [],
    }
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
        report["auth_query_keys"] = sorted(args)
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
            raise RuntimeError("Missing public session token")
        endpoint = BASE + f"/aspera/faspex/api/v5/packages/{PACKAGE_ID}/files/received/page?offset=0&limit=1000"
        paths = ["/"]
        for depth in range(2):
            folder = paths[depth]
            status, raw = post_json(opener, endpoint, {"path": folder}, token)
            item = {"path": folder, "http_status": status, "response_bytes": len(raw),
                    "response_sha256": hashlib.sha256(raw).hexdigest()}
            report["listings"].append(item)
            if status not in (200, 201):
                break
            listing = json.loads(raw)
            data = listing.get("data", listing)
            entries = data.get("items", [])
            item["item_count"] = data.get("item_count")
            item["entries"] = [
                {key: entry.get(key) for key in ("name", "path", "type", "size", "is_dir") if key in entry}
                for entry in entries[:1000]
            ]
            item["entries_returned"] = len(entries)
            if len(entries) >= 1000:
                item["truncated_by_limit"] = True
            if depth == 0:
                directories = [entry["path"] for entry in item["entries"]
                               if entry.get("type") == "directory" or entry.get("is_dir") is True]
                if len(directories) != 1 or not directories[0].startswith("/"):
                    break
                paths.append(directories[0])
    except (KeyError, ValueError, RuntimeError, urllib.error.URLError, TimeoutError) as error:
        report["error_type"] = type(error).__name__
        report["error_stage"] = "public_auth_or_listing"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "listings"} |
                     {"listings": [{key: value for key, value in item.items() if key != "entries"}
                                   for item in report["listings"]]}, indent=2))


if __name__ == "__main__":
    main()
