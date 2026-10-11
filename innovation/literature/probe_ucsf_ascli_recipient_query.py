"""Read-only test of the extra recipient query used by IBM ascli Faspex5."""

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
PREFLIGHT = HERE / "source_cache" / "ucsf_two_file_transfer_spec_probe_2026-10-01.json"
OUT = HERE / "source_cache" / "ucsf_ascli_recipient_query_probe_2026-10-01.json"


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if not preflight["spec_scope_pass"]:
        raise ValueError("Original exact two-file preflight failed")
    paths = preflight["requested_paths"]
    page = Links()
    page.feed(OFFICIAL.read_text(encoding="utf-8"))
    contexts = []
    for link in page.hrefs:
        if link.startswith(BASE + "/aspera/faspex?"):
            context = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query).get("context", [None])[0]
            if context and json.loads(base64.b64decode(context).decode()).get("id") == "1065":
                contexts.append(context)
    if len(contexts) != 1:
        raise ValueError("Unexpected public link count")
    report = {"package_id": "1065", "requested_path_count": len(paths),
              "preflight_sha256": hashlib.sha256(PREFLIGHT.read_bytes()).hexdigest(),
              "transfer_started": False, "patient_pixels_read": False,
              "secret_or_spec_archived": False}
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect()
    )
    authorize = BASE + "/aspera/faspex/auth/authorize_public_link?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI, "state": contexts[0],
    })
    try:
        opener.open(urllib.request.Request(authorize, headers={"User-Agent": "MRI-source-audit/1.0"}), timeout=35)
        raise RuntimeError("Expected authorization redirect")
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise RuntimeError("Public authorization failed") from None
        redirect = urllib.parse.urlsplit(error.headers["Location"])
    args = urllib.parse.parse_qs(redirect.query)
    status, raw = post_json(opener, BASE + "/aspera/faspex/auth/token", {
        "code": args["code"][0], "state": args.get("state", [""])[0],
        "grant_type": "authorization_code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    })
    if status not in (200, 201):
        raise RuntimeError("Public token exchange failed")
    data = json.loads(raw)
    token = data.get("data", data)["access_token"]
    package_url = BASE + "/aspera/faspex/api/v5/packages/1065"
    request = urllib.request.Request(package_url, headers={"Authorization": token,
                                                           "Accept": "application/json",
                                                           "User-Agent": "MRI-source-audit/1.0"})
    with opener.open(request, timeout=25) as response:
        package = json.loads(response.read(500_000))
        report["package_http_status"] = response.status
    package_data = package.get("data", package)
    recipients = package_data.get("recipients", [])
    if not recipients:
        raise RuntimeError("No package recipients in public response")
    recipient = recipients[0]
    kind = recipient.get("recipient_type")
    recipient_id = recipient.get("id")
    report["first_recipient_type"] = kind
    report["first_recipient_id_present"] = recipient_id is not None
    query = {"transfer_type": "connect", "type": "received"}
    if kind in ("workgroup", "shared_inbox"):
        query["recipient_workgroup_id"] = recipient_id
    elif kind == "user":
        query["recipient_user_id"] = recipient_id
    report["extra_query_keys"] = sorted(set(query) - {"transfer_type", "type"})
    endpoint = package_url + "/transfer_spec/download?" + urllib.parse.urlencode(query)
    status, raw = post_json(opener, endpoint, {"paths": [{"path": path} for path in paths]}, token)
    report["spec_http_status"] = status
    report["response_bytes"] = len(raw)
    report["response_sha256"] = hashlib.sha256(raw).hexdigest()
    if status in (200, 201):
        body = json.loads(raw)
        result = body.get("data", body)
        spec = result.get("transfer_spec", result)
        report["spec_path_count"] = len(spec.get("paths", []))
        report["spec_paths_match_requested"] = all(
            item.get("source", "").endswith(path)
            for item, path in zip(spec.get("paths", []), paths)
        )
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
