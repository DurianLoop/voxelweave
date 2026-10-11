"""Request but do not execute a scoped UCSF public-link Connect transfer spec."""

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
CASE_LIST = HERE / "source_cache" / "ucsf_pdgm_005_file_list_2026-10-01.json"
OUT = HERE / "source_cache" / "ucsf_two_file_transfer_spec_probe_2026-10-01.json"
NAMES = ("UCSF-PDGM-0005_T2.nii.gz", "UCSF-PDGM-0005_tumor_segmentation.nii.gz")


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    case = json.loads(CASE_LIST.read_text(encoding="utf-8"))
    if case.get("case_csv_id") != "UCSF-PDGM-005" or case.get("http_status") != 200:
        raise ValueError("Frozen official case listing is unavailable")
    selected = []
    for name in NAMES:
        matches = [entry for entry in case["entries"] if entry["path"].endswith("/" + name)]
        if len(matches) != 1 or matches[0].get("type") != "symbolic_link":
            raise ValueError(f"Unexpected frozen member: {name}")
        selected.append(matches[0])
    paths = [entry["path"] for entry in selected]
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
        raise ValueError("Unexpected public link count")
    report = {"package_id": "1065", "case_csv_id": "UCSF-PDGM-005",
              "requested_paths": paths, "declared_bytes": [entry["size"] for entry in selected],
              "case_listing_sha256": hashlib.sha256(CASE_LIST.read_bytes()).hexdigest(),
              "transfer_started": False, "patient_pixels_read": False,
              "secret_or_spec_archived": False}
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect()
    )
    try:
        authorize = BASE + "/aspera/faspex/auth/authorize_public_link?" + urllib.parse.urlencode({
            "response_type": "code", "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI, "state": contexts[0],
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
        token_body = json.loads(raw)
        token = token_body.get("data", token_body).get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Missing public session")
        endpoint = BASE + "/aspera/faspex/api/v5/packages/1065/transfer_spec/download?transfer_type=connect&type=received"
        status, raw = post_json(opener, endpoint, {"paths": [{"path": path} for path in paths]}, token)
        report["spec_http_status"] = status
        report["spec_response_bytes"] = len(raw)
        report["spec_response_sha256"] = hashlib.sha256(raw).hexdigest()
        if status not in (200, 201):
            raise RuntimeError("Two-file transfer spec request failed")
        body = json.loads(raw)
        data = body.get("data", body)
        spec = data.get("transfer_spec", data)
        sources = [entry.get("source") for entry in spec.get("paths", [])]
        report["spec_path_count"] = len(sources)
        report["paths_match_requested_suffixes"] = len(sources) == 2 and all(
            isinstance(source, str) and source.endswith(path)
            for source, path in zip(sources, paths)
        )
        report["source_root_null"] = spec.get("source_root") is None
        report["zip_required"] = spec.get("zip_required")
        report["direction"] = spec.get("direction")
        report["authentication_kind"] = spec.get("authentication")
        report["credential_fields_present"] = bool(spec.get("token")) and bool(spec.get("cookie"))
        report["spec_scope_pass"] = bool(
            report["paths_match_requested_suffixes"] and report["source_root_null"]
            and report["zip_required"] is not True and report["direction"] == "receive"
            and report["authentication_kind"] == "token"
        )
    except (KeyError, ValueError, RuntimeError, urllib.error.URLError, TimeoutError) as error:
        report["error_type"] = type(error).__name__
        report["error_stage"] = "public_auth_or_spec"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
