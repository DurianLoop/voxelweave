"""Use Faspex's published public-link flow only to list package root files."""

from __future__ import annotations

import base64
import hashlib
import http.cookiejar
import json
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OFFICIAL = ROOT / "source_cache" / "upenn_gbm_collection_page_2026-10-01.html"
OUT = ROOT / "source_cache" / "upenn_gbm_public_package_tree_v7_2026-10-01.json"
BASE = "https://faspex.cancerimagingarchive.net"
CLIENT_ID = "ff9aa63a-72e1-436f-82ef-5677eb1f7aee"
REDIRECT_URI = BASE + "/aspera/faspex/token"


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def post_json(opener, url: str, payload: dict, token: str | None = None) -> tuple[int, bytes]:
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "User-Agent": "MRI-source-audit/1.0"}
    if token:
        headers["Authorization"] = token
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    try:
        with opener.open(request, timeout=90) as response:
            return response.status, response.read(2_000_001)
    except urllib.error.HTTPError as error:
        return error.code, error.read(1000)


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUT}")
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    public_url = next(u for u in page.hrefs if u.startswith(BASE + "/aspera/faspex/public/package?"))
    context = urllib.parse.parse_qs(urllib.parse.urlsplit(public_url).query)["context"][0]
    details = json.loads(base64.b64decode(context).decode())
    if details.get("type") != "external_download_package" or details.get("id") != "604":
        raise ValueError("Unexpected public package context")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar), NoRedirect())
    authorize = BASE + "/aspera/faspex/auth/authorize_public_link?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI, "state": context,
    })
    request = urllib.request.Request(authorize, headers={"User-Agent": "MRI-source-audit/1.0"})
    try:
        with opener.open(request, timeout=35) as response:
            auth_status, location = response.status, response.headers.get("Location", "")
    except urllib.error.HTTPError as error:
        auth_status, location = error.code, error.headers.get("Location", "")
    report = {"official_link_sha256": hashlib.sha256(public_url.encode()).hexdigest(),
              "auth_http_status": auth_status,
              "auth_redirect_path": urllib.parse.urlsplit(location).path if location else None,
              "auth_query_keys": sorted(urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)),
              "package_transfer_started": False, "patient_pixels_read": False}
    parsed = urllib.parse.urlsplit(location)
    redirect_args = urllib.parse.parse_qs(parsed.query)
    if auth_status not in (301, 302, 303, 307, 308) or parsed.path != "/aspera/faspex/token" or "code" not in redirect_args:
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return
    status, token_body = post_json(opener, BASE + "/aspera/faspex/auth/token", {
        "code": redirect_args["code"][0],
        "state": redirect_args.get("state", [""])[0],
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    })
    report["token_http_status"] = status
    if status not in (200, 201):
        report["token_error_sha256"] = hashlib.sha256(token_body).hexdigest()
    else:
        token_result = json.loads(token_body)
        token_data = token_result.get("data", token_result)
        token = token_data.get("access_token")
        if not isinstance(token, str) or not token:
            report["token_response_keys"] = sorted(token_result)
        else:
            report["token_acquired"] = True
            endpoint = BASE + "/aspera/faspex/api/v5/packages/604/files/received/page?offset=0&limit=1000"
            report["listings"] = []
            for folder in ("/UPENN-GBM/NIfTI-files/automated_segm",
                           "/UPENN-GBM/NIfTI-files/images_structural/UPENN-GBM-00001_11",
                           "/UPENN-GBM/NIfTI-files/images_structural/UPENN-GBM-00002_11"):
                list_status, body = post_json(opener, endpoint, {"path": folder}, token)
                item = {"path": folder, "http_status": list_status,
                        "response_bytes": len(body),
                        "response_sha256": hashlib.sha256(body).hexdigest()}
                if list_status in (200, 201):
                    listing = json.loads(body)
                    item["response_keys"] = sorted(listing)
                    data = listing.get("data", listing)
                    if isinstance(data, dict):
                        item["item_count"] = data.get("item_count")
                        item["total_count"] = data.get("total_count")
                        entries = data.get("items", [])
                    else:
                        entries = data if isinstance(data, list) else []
                    item["entries"] = [
                        {field: entry.get(field) for field in ("name", "path", "type", "size", "is_dir") if field in entry}
                        for entry in entries[:1000]
                    ]
                    item["entries_returned"] = len(entries)
                report["listings"].append(item)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"auth_http_status": report["auth_http_status"],
                      "token_http_status": report.get("token_http_status"),
                      "listings": [
                          {key: value for key, value in item.items() if key != "entries"}
                          for item in report.get("listings", [])
                      ]}, indent=2))


if __name__ == "__main__":
    main()
