"""Read a few public MSValid T2 NIfTI headers through remote ZIP ranges."""
from __future__ import annotations

import argparse
import gzip
import io
import json
import zipfile
from pathlib import Path

import nibabel as nib

from msvalid_remote_inventory import RemoteZip


ROOT = Path(__file__).resolve().parent
INDEX = json.loads((ROOT / "msvalid_remote_inventory.json").read_text(encoding="utf-8"))
PATIENTS = ("P1", "P2", "P3", "P4", "P5", "P50", "P84")
OUT = ROOT / "msvalid_header_probe.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-first-t2", action="store_true")
    args = parser.parse_args()
    patients = (sorted({member["path"].split("/")[1] for member in INDEX["members"]
                        if member["path"].startswith("MSValid/")
                        and member["path"].endswith("_T2.nii.gz")},
                       key=lambda value: int(value[1:])) if args.all_first_t2 else PATIENTS)
    remote = RemoteZip()
    results = []
    with zipfile.ZipFile(remote) as archive:
        for patient in patients:
            names = sorted(member["path"] for member in INDEX["members"]
                           if member["path"].startswith(f"MSValid/{patient}/")
                           and member["path"].endswith("_T2.nii.gz"))
            if not names:
                results.append({"patient": patient, "error": "no_T2_file"})
                continue
            name = names[0]
            try:
                with archive.open(name) as zipped, gzip.GzipFile(fileobj=zipped) as nifti:
                    header_bytes = nifti.read(352)
                header = nib.Nifti1Header.from_fileobj(io.BytesIO(header_bytes))
                results.append({"patient": patient, "member": name,
                                "shape": list(header.get_data_shape()),
                                "zooms_mm": [float(v) for v in header.get_zooms()],
                                "qform_code": int(header["qform_code"]),
                                "sform_code": int(header["sform_code"]),
                                "datatype": str(header.get_data_dtype())})
            except (OSError, EOFError, ValueError, zipfile.BadZipFile) as error:
                results.append({"patient": patient, "member": name,
                                "error": f"{type(error).__name__}: {error}"})
            if not args.all_first_t2 or len(results) % 10 == 0:
                print(f"header {len(results)}/{len(patients)} "
                      + json.dumps(results[-1], ensure_ascii=False), flush=True)
    result = {"source": INDEX["source"], "metadata_only_bytes_transferred": remote.transferred,
              "samples": results,
              "limitation": "Headers identify native geometry but do not verify image quality, scan protocol, or patient independence."}
    output = ROOT / ("msvalid_header_all.json" if args.all_first_t2 else OUT.name)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("range_bytes", remote.transferred)


if __name__ == "__main__":
    main()
