"""Archive the exact experiment rows present in the current master table."""

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import statistics
import subprocess
import time
import zipfile
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "docx/experiment/experiment_master_table.md"
METRICS = ("psnr", "ssim", "mae", "mse", "ncc")
OUT = ROOT / "exports/experiment_master_table_weights_2026-09-20"


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag == "td":
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = None


def method_key(name):
    name = name.lower()
    for needle, key in [("pastnet", "pastnet"), ("ressrdiff", "ressrdiff"),
                        ("gan_2p5d", "gan_2p5d"),
                        ("past-net", "pastnet"), ("res-srdiff", "ressrdiff"),
                        ("pix2pix", "gan_2p5d"), ("smamba", "smamba_unet"),
                        ("resunet", "resunet"), ("swinir", "swinir"),
                        ("cycleinr", "cycleinr"), ("arssr", "arssr"),
                        ("acvtt", "acvtt"), ("saint", "saint"),
                        ("i3net", "i3net"), ("hat", "hat"),
                        ("linear", "linear"), ("cubic", "cubic")]:
        if needle in name:
            return key
    raise ValueError(name)


def table_entries():
    contents = TABLE.read_text(encoding="utf-8-sig")
    parser = TableParser()
    parser.feed(contents)
    rows = []

    def add(section, dataset, scale, name, values):
        rows.append(dict(id=f"R{len(rows)+1:03d}", section=section, dataset=dataset,
                         scale=scale, method=method_key(name), label=name,
                         metrics=dict(zip(METRICS, map(float, values)))))

    for row in parser.rows:
        if row[0] == "x4":
            row = row[1:]
        assert len(row) == 16, row
        for i, dataset in enumerate(("IXI", "fastMRI", "NingXia")):
            add("main_x4", dataset, 4, row[0], row[1+5*i:6+5*i])
    section = ""
    for line in contents.splitlines():
        if line.startswith("##"):
            if "PAST-Net fastMRI" in line:
                section = "pastnet_development"
            elif "90-Epoch" in line:
                section = "ningxia_90"
            elif "60-Epoch" in line:
                section = "ningxia_60" if "NingXia" in line else "fastmri_60"
            elif "fastMRI-brain-T2 expanded" in line:
                section = "fastmri_multiscale"
            elif "NingXia-T2" in line:
                section = "ningxia_multiscale"
            else:
                section = ""
        if not line.startswith("|") or not section:
            continue
        cells = [c.strip().replace("**", "") for c in line.strip("|").split("|")]
        if section == "pastnet_development" and cells[0].startswith("PAST-Net"):
            add(section, "fastMRI", 4, cells[0], cells[1:6])
        elif cells[0] in ("x2", "x4", "x6"):
            add(section, "NingXia" if section.startswith("ningxia") else "fastMRI",
                int(cells[0][1:]), cells[1], cells[2:7])
    return rows


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def rel(path):
    return path.relative_to(ROOT).as_posix()


def candidate_groups():
    result = subprocess.run(
        ["rg", "--files", "--hidden", "--no-ignore", "baseline", "pre",
         "design/fastmri_brain_pastnet_2p5d", "-g", "summary_metrics.csv"],
        cwd=ROOT, check=True, capture_output=True, text=True)
    groups = defaultdict(list)
    for name in result.stdout.splitlines():
        path = ROOT / name
        parts = Path(name).parts
        package = parts[1]
        dataset = next((ds for prefix, ds in [("ixi", "IXI"), ("fastmri", "fastMRI"),
                                             ("ningxia", "NingXia")]
                        if package.startswith(prefix)), None)
        if not dataset or "runs" not in parts:
            continue
        run = path.parent.parent
        profile = run.name
        fold = run.parent.name if run.parent.name.startswith("fold_") else ""
        if dataset == "NingXia" and not fold:
            continue
        manifest = run / "run_manifest.json"
        config = json.loads(manifest.read_text(encoding="utf-8-sig")) if manifest.exists() else {}
        scale_match = re.search(r"(?:^|_)x([246])(?:_|$)", profile)
        scale = int(config.get("stride") or (scale_match.group(1) if scale_match else 4))
        for row in read_csv(path):
            key = row.get("method", "")
            if key in ("linear", "cubic") or not key:
                continue
            try:
                key = method_key(key)
            except ValueError:
                continue
            metrics = {m: float(row[m + "_mean"]) for m in METRICS}
            group = (dataset, scale, key, rel(run.parent.parent if fold else run.parent), profile)
            groups[group].append(dict(summary=rel(path), run=rel(run), fold=fold,
                                      cases=int(row["cases"]), metrics=metrics))
    candidates = []
    for (dataset, scale, key, base, profile), runs in groups.items():
        if dataset == "NingXia" and sorted(r["fold"] for r in runs) != [f"fold_{i:02d}" for i in range(8)]:
            continue
        candidates.append(dict(dataset=dataset, scale=scale, method=key, base=base,
                               profile=profile, runs=runs,
                               metrics={m: statistics.mean(r["metrics"][m] for r in runs) for m in METRICS}))
    recovered = ROOT / "design/paper/PLAN15_BASELINE_INTEGRATION/outputs/saint_recovered_summary.csv"
    for row in read_csv(recovered):
        profile = "full_x" + row["scale"]
        run = "baseline/fastmri_brain_saint/runs/" + profile
        metrics = {m: float(row[m]) for m in METRICS}
        candidates.append(dict(dataset="fastMRI", scale=int(row["scale"]), method="saint",
                               base="baseline/fastmri_brain_saint/runs", profile=profile,
                               recovered_evidence=True, metrics=metrics,
                               runs=[dict(summary=rel(recovered), run=run, fold="", cases=24,
                                          metrics=metrics)]))
    return candidates


def inventory():
    rows = table_entries()
    candidates = candidate_groups()
    for row in rows:
        if row["method"] in ("linear", "cubic"):
            row.update(status="non_learned", candidates=[])
            continue
        matches = [c for c in candidates
                   if all(c[k] == row[k] for k in ("dataset", "scale", "method"))
                   and all(abs(c["metrics"][m] - row["metrics"][m]) < 0.0000501 for m in METRICS)]
        row["candidates"] = matches
        row["status"] = "matched" if len(matches) == 1 else "ambiguous" if matches else "unmatched"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "inventory.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = defaultdict(int)
    for row in rows:
        counts[row["status"]] += 1
        if row["status"] not in ("matched", "non_learned"):
            print(row["id"], row["dataset"], row["scale"], row["label"], row["section"], row["status"],
                  [(c["base"], c["profile"]) for c in row["candidates"]])
    print("TABLE_ROWS", len(rows), "STATUS", dict(counts))
    print("CANDIDATES", len(candidates))
    return rows


def checkpoint_plan(rows):
    records = []
    missing = []
    for row in rows:
        if row["status"] == "non_learned":
            continue
        if row["status"] != "matched":
            missing.append(row["id"] + ": " + row["status"])
            continue
        candidate = row["candidates"][0]
        for run_info in candidate["runs"]:
            run = ROOT / run_info["run"]
            train_run = run
            source = "same_run_best"
            if row["dataset"] == "IXI" and row["method"] in ("arssr", "cycleinr", "swinir", "resunet", "saint"):
                train_profile = {"resunet": "resunet_full_t2", "saint": "saint_full_t2"}.get(row["method"], "full")
                train_run = run.parent / train_profile
                source = "eval_only_reuse_documented_in_master"
            prefix = "gan" if row["method"] == "gan_2p5d" else row["method"]
            choices = list((train_run / "checkpoints").glob(prefix + "*best*.pth"))
            if len(choices) != 1:
                missing.append(f"{row['id']} {run_info['fold']} {train_run}: {choices}")
                continue
            path = choices[0]
            record = dict(table_row=row["id"], section=row["section"], dataset=row["dataset"],
                          scale=row["scale"], method=row["method"], label=row["label"],
                          evaluation_profile=candidate["profile"], training_profile=train_run.name,
                          fold=run_info["fold"], evaluation_cases=run_info["cases"],
                          checkpoint=rel(path), bytes=path.stat().st_size,
                          evaluation_run=rel(run), training_run=rel(train_run),
                          summary=run_info["summary"], mapping_basis=source,
                          recovered_evidence=bool(candidate.get("recovered_evidence")),
                          table_metrics=row["metrics"], run_metrics=run_info["metrics"])
            records.append(record)
    data = dict(records=records, missing=missing)
    (OUT / "checkpoint_plan.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("CHECKPOINTS", len(records), "UNIQUE", len({r["checkpoint"] for r in records}),
          "GiB", round(sum(r["bytes"] for r in records) / 2**30, 3), "MISSING", missing)
    return data


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit_checkpoints(plan):
    import torch

    torch.set_num_threads(1)
    audits = {}
    for i, record in enumerate(plan["records"], 1):
        path = ROOT / record["checkpoint"]
        payload = torch.load(path, map_location="cpu", weights_only=True)
        if not isinstance(payload, dict):
            raise TypeError(f"Expected checkpoint dictionary: {path}")
        states = {k: v for k, v in payload.items() if isinstance(v, dict) and "state_dict" in k}
        required = "generator_state_dict" if record["method"] == "gan_2p5d" else "model_state_dict"
        if required not in states or not states[required]:
            raise ValueError(f"Missing {required}: {path}")
        tensors = [v for state in states.values() for v in state.values() if torch.is_tensor(v)]
        if not tensors:
            raise ValueError(f"No weight tensors: {path}")
        metadata = {}
        for key, value in payload.items():
            if "state_dict" in key:
                continue
            try:
                json.dumps(value, allow_nan=False)
            except (TypeError, ValueError):
                continue
            metadata[key] = value
        audit = dict(checkpoint=record["checkpoint"], sha256=sha256(path), bytes=path.stat().st_size,
                     load_status="weights_only_cpu_ok", payload_keys=list(payload),
                     state_dict_keys=list(states), tensor_count=len(tensors),
                     tensor_elements=sum(t.numel() for t in tensors), metadata=metadata)
        stride = metadata.get("stride")
        if stride is not None and int(stride) != record["scale"]:
            raise ValueError(f"Checkpoint scale mismatch: {path}: {stride} != {record['scale']}")
        record["sha256"] = audit["sha256"]
        record["checkpoint_epoch"] = metadata.get("epoch")
        record["checkpoint_best_val_loss"] = metadata.get("best_val_loss")
        record["load_status"] = audit["load_status"]
        audits[record["checkpoint"]] = audit
        del payload, states, tensors
        if i % 40 == 0 or i == len(plan["records"]):
            print(f"CHECKPOINT_AUDIT {i}/{len(plan['records'])}", flush=True)
    (OUT / "checkpoint_metadata.json").write_text(json.dumps(audits, ensure_ascii=False, indent=2), encoding="utf-8")
    return audits


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def write_indexes(rows, plan):
    index = []
    for record in plan["records"]:
        index.append({k: json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v
                      for k, v in record.items()})
        index[-1]["archive_path"] = "project/" + record["checkpoint"]
    (OUT / "checkpoint_index.csv").write_bytes(csv_bytes(index))
    counts = defaultdict(int)
    for record in plan["records"]:
        counts[record["section"]] += 1
    table_index = []
    lines = ["# 主表与权重对应清单", "", "日期：2026-09-20。每项指标按照主表显示精度核对。",
             "NingXia 每行目录下包含 fold_00 至 fold_07 八份权重，详细文件及 SHA256 见 checkpoint_index.csv。",
             "训练与评估目录分别记录；eval-only 不能误用评估目录中的其他权重。", "",
             "| ID | 表格分区 | 数据集 | 倍率 | 方法 | 训练 profile | 权重数 | 训练目录 | 说明 |",
             "|---|---|---|---|---|---|---:|---|---|"]
    for row in rows:
        records = [r for r in plan["records"] if r["table_row"] == row["id"]]
        item = {k: v for k, v in row.items() if k != "candidates"}
        item["checkpoint_count"] = len(records)
        item["checkpoints"] = [r["checkpoint"] for r in records]
        table_index.append(item)
        if not records:
            note, profile, location = "非学习插值，无模型权重", "-", "-"
        else:
            first = records[0]
            note = "五指标来源匹配"
            if first["mapping_basis"] != "same_run_best":
                note += "；复用 full best 做 n=115 测试"
            if first["recovered_evidence"]:
                note = "SAINT 指标来自既有预测恢复审计；共享目录配置可能属于 ResUNet"
            profile = first["training_profile"]
            location = first["training_run"]
            if len(records) == 8:
                location = location.replace("fold_00", "fold_00..07")
        lines.append(f"| {row['id']} | {row['section']} | {row['dataset']} | x{row['scale']} | {row['label']} | `{profile}` | {len(records)} | `{location}` | {note} |")
    (OUT / "CHECKPOINT_CATALOG_ZH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "table_index.json").write_text(json.dumps(table_index, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "checkpoint_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SECTION_COUNTS", dict(counts), flush=True)


def collect_files(plan):
    selected = set()
    for record in plan["records"]:
        selected.add(ROOT / record["checkpoint"])
        selected.add(ROOT / record["summary"])
        for key in ("evaluation_run", "training_run"):
            run = ROOT / record[key]
            for name in ("run_manifest.json", "training_history.csv", "training_history.json"):
                path = run / name
                if path.exists():
                    selected.add(path)
            for name in ("per_case_metrics.csv", "summary_metrics.csv", "summary_metrics.json", "paper_table.md"):
                path = run / "metrics" / name
                if path.exists():
                    selected.add(path)
    # Only source/config files, never raw images, predictions, or unlisted weights.
    scopes = ["baseline", "pre", "processing", "design/fastmri_brain_pastnet_2p5d",
              "design/ixi_pastnet_2p5d", "external/I3Net", "external/ACVTT", "external/Res-SRDiff"]
    result = subprocess.run(["rg", "--files", "--hidden", "--no-ignore", *scopes,
                             "-g", "*.py", "-g", "*.yaml", "-g", "*.yml",
                             "-g", "*requirements*.txt", "-g", "LICENSE*",
                             "-g", "!**/runs/**", "-g", "!**/.git/**", "-g", "!**/__pycache__/**"],
                            cwd=ROOT, check=True, capture_output=True, text=True)
    selected.update(ROOT / name for name in result.stdout.splitlines())
    for name in ("requirements.txt", "environment.yml", "docx/experiment/experiment_master_table.md",
                 "docx/experiment_notes/full_test115_completion_summary_20260703.md",
                 "handoff_hat_smamba_evidence_2026-09-16/AUDIT_REPORT.md",
                 "handoff_hat_smamba_evidence_2026-09-16/checkpoint_audit.csv",
                 "design/paper/PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md",
                 "design/paper/PLAN15_BASELINE_INTEGRATION/outputs/saint_recovered_per_case.csv",
                 "design/paper/PLAN15_BASELINE_INTEGRATION/outputs/saint_recovery_manifest.json"):
        selected.add(ROOT / name)
    files = {"project/" + rel(path): path for path in sorted(selected)}
    for name in ("README_ZH.md", "CHECKPOINT_CATALOG_ZH.md", "checkpoint_index.csv",
                 "checkpoint_metadata.json", "table_index.json", "checkpoint_plan.json", "inventory.json"):
        files[name] = OUT / name
    return files


def build_archive(rows, plan):
    if plan["missing"]:
        raise ValueError(f"Unresolved mappings: {plan['missing']}")
    audit_checkpoints(plan)
    write_indexes(rows, plan)
    files = collect_files(plan)
    total = sum(p.stat().st_size for p in files.values())
    if shutil.disk_usage(OUT).free < total * 1.05 + 2**30:
        raise OSError("Insufficient free space for archive and safety margin")
    archive = OUT.with_suffix(".zip")
    partial = Path(str(archive) + ".partial")
    if archive.exists() or partial.exists():
        raise FileExistsError(f"Refusing to overwrite an archive: {archive}")
    expected_weights = {"project/" + r["checkpoint"]: r["sha256"] for r in plan["records"]}
    manifests = []
    last_progress = time.monotonic()
    written = 0
    print(f"ARCHIVE_START files={len(files)} bytes={total} output={archive}", flush=True)
    with zipfile.ZipFile(partial, "x", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as zf:
        for i, (name, path) in enumerate(sorted(files.items()), 1):
            before = path.stat()
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as src, zf.open(name, "w", force_zip64=True) as dst:
                while chunk := src.read(4 * 1024**2):
                    digest.update(chunk)
                    size += len(chunk)
                    dst.write(chunk)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise RuntimeError(f"Source changed while archiving: {path}")
            checksum = digest.hexdigest()
            if name in expected_weights and expected_weights[name] != checksum:
                raise RuntimeError(f"Checkpoint changed after audit: {path}")
            manifests.append(dict(archive_path=name, bytes=size, sha256=checksum))
            written += size
            if time.monotonic() - last_progress > 20 or i == len(files):
                print(f"ARCHIVE_WRITE {i}/{len(files)} {written/2**30:.2f}/{total/2**30:.2f} GiB", flush=True)
                last_progress = time.monotonic()
        manifest_data = csv_bytes(manifests)
        zf.writestr("file_manifest.csv", manifest_data)
    (OUT / "file_manifest.csv").write_bytes(manifest_data)
    print("ARCHIVE_VERIFY_START", flush=True)
    last_progress = time.monotonic()
    verified = 0
    with zipfile.ZipFile(partial, "r") as zf:
        if len(zf.namelist()) != len(set(zf.namelist())):
            raise ValueError("Duplicate archive member names")
        assert len(zf.namelist()) == len(manifests) + 1
        for i, item in enumerate(manifests, 1):
            with zf.open(item["archive_path"]) as stream:
                checksum = hashlib.file_digest(stream, "sha256").hexdigest()
            if checksum != item["sha256"]:
                raise ValueError(f"Readback hash mismatch: {item['archive_path']}")
            verified += item["bytes"]
            if time.monotonic() - last_progress > 20 or i == len(manifests):
                print(f"ARCHIVE_VERIFY {i}/{len(manifests)} {verified/2**30:.2f} GiB", flush=True)
                last_progress = time.monotonic()
        assert zf.read("file_manifest.csv") == manifest_data
    partial.rename(archive)
    checksum = sha256(archive)
    Path(str(archive) + ".sha256").write_text(checksum + "  " + archive.name + "\n", encoding="ascii")
    report = dict(archive=str(archive), archive_bytes=archive.stat().st_size,
                  archive_sha256=checksum, source_table_sha256=sha256(TABLE),
                  table_rows=len(rows), learned_rows=sum(r["status"] != "non_learned" for r in rows),
                  weight_count=len(expected_weights), missing=plan["missing"],
                  content_files=len(manifests), sha256_verified_files=len(manifests),
                  file_manifest_verified=True, checkpoint_cpu_load_verified=True,
                  gpu_used=False, status="PASS")
    (OUT / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    rows = inventory()
    plan = checkpoint_plan(rows)
    if args.build:
        build_archive(rows, plan)
