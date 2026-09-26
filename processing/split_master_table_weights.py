"""Create independent, size-limited ZIPs from the verified weight archive."""

import argparse
import csv
import hashlib
import io
import json
import shutil
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "exports/experiment_master_table_weights_2026-09-20.zip"
CHUNK_SIZE = 4 * 1024**2


def digest_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def csv_data(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def read_csv(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def assign_groups(records, part_count):
    groups = defaultdict(list)
    for record in records:
        groups[record["table_row"]].append(record)
    bins = [dict(number=i + 1, bytes=0, records=[]) for i in range(part_count)]
    # Keep every table row, including all eight CV folds, together.
    ordered = sorted(groups.items(), key=lambda item: (-sum(int(r["bytes"]) for r in item[1]), item[0]))
    for _, group in ordered:
        target = min(bins, key=lambda part: (part["bytes"], part["number"]))
        target["records"].extend(group)
        target["bytes"] += sum(int(r["bytes"]) for r in group)
    return bins


def readme_text(source_name, bins, max_bytes):
    lines = [
        "# 模型权重分包说明", "",
        f"原完整归档：`{source_name}`。本次拆为 {len(bins)} 个普通 ZIP，",
        f"每包文件大小严格小于 **{max_bytes:,} 字节（十进制 {max_bytes / 10**9:g} GB）**。", "",
        "## 上传和解压", "",
        "1. 分别上传下列全部 ZIP，不需要上传原来的 6.61 GiB 完整 ZIP。",
        "2. 每个 ZIP 均可独立打开、独立解压，不是 .z01 分卷，不需要拼接二进制文件。",
        "3. 需要完整集合时，将全部 ZIP 解压到同一个空目录。公共说明、代码和指标文件内容一致，重复文件可覆盖或跳过。",
        "4. 每份权重只出现在一个包中。同一主表实验项的 NingXia 8 折权重不会拆散。", "",
        "## 分包清单", "",
        "| ZIP 文件 | 权重数 | 对应学习实验项数 |",
        "|---|---:|---:|",
    ]
    for part in bins:
        lines.append(f"| `{part['filename']}` | {len(part['records'])} | {len({r['table_row'] for r in part['records']})} |")
    lines.extend([
        "", "合计 **458 份 best checkpoint，108 项学习模型结果**，与原完整 ZIP 一致。",
        "原 ZIP 和工作区模型文件保持不动；本次直接从已校验的原 ZIP 读取，不重新训练，不调用 GPU。", "",
        "## 包内文件", "",
        "- `README_ZH.md`：本分包说明，每包相同。",
        "- `README_FULL_ARCHIVE_ZH.md`：原完整权重包的中文说明，包含历史记录和科学有效性边界。",
        "- `part_assignment.csv`：全部权重到 ZIP 文件的对应关系，可按方法、倍率、数据集筛选。",
        "- `partNN_checkpoint_index.csv`：当前包专属的权重清单。",
        "- `partNN_file_manifest.csv`：当前包文件的 SHA256 和大小；不包含该清单自身。",
        "- `checkpoint_index.csv`、`CHECKPOINT_CATALOG_ZH.md` 等：原完整归档的总索引，描述全部四包，不代表当前单包有全部权重。",
        "- `FULL_ARCHIVE_file_manifest.csv`：原完整 ZIP 的文件清单，仅用于追溯原包，不用于检查单个分包。",
        "- `project/`：保持原相对路径。权重分配到各包，其余代码、配置、指标、日志均在每包中重复提供。", "",
        "## 完整性", "",
        "生成时先核对原 ZIP 的 SHA256，再核对每份文件内容；每包写完后逐文件回读，验证 SHA256 和 ZIP CRC。",
        "外部 `split_validation_report.json` 记录四包实际大小、整包 SHA256、458 份权重不遗漏不重复等检查结果。",
        "同目录还有 `SHA256SUMS.txt` 和各 ZIP 的 `.sha256` 文件。上传后可据此核对下载文件。", "",
        "未包含 MRI 原始影像和预测。运行记录可能含病例/序列标识；公开发布前请按原说明审查匿名化和许可证。", "",
    ])
    return "\n".join(lines)


def split_archive(source, output, part_count, max_bytes):
    output.mkdir(parents=True, exist_ok=True)
    source_stat = source.stat()
    expected_archive_hash = Path(str(source) + ".sha256").read_text(encoding="ascii").split()[0]
    source_hash = digest_file(source)
    if source_hash != expected_archive_hash:
        raise ValueError("Source ZIP SHA256 does not match its checksum file")
    print("SOURCE_SHA256_PASS", flush=True)
    source_to_part = {}
    results = []
    with zipfile.ZipFile(source) as original:
        infos = {entry.filename: entry for entry in original.infolist()}
        if len(infos) != len(original.infolist()):
            raise ValueError("Duplicate source ZIP members")
        records = read_csv(original.read("checkpoint_index.csv"))
        if len(records) != 458:
            raise ValueError("Unexpected source checkpoint count")
        weight_names = [r["archive_path"] for r in records]
        if len(set(weight_names)) != len(weight_names):
            raise ValueError("Duplicate checkpoint paths")
        if {n for n in infos if n.endswith(".pth")} != set(weight_names):
            raise ValueError("Unindexed or missing checkpoints")
        original_manifest = {r["archive_path"]: r for r in read_csv(original.read("file_manifest.csv"))}
        if set(original_manifest) != set(infos) - {"file_manifest.csv"}:
            raise ValueError("Source manifest does not cover all files")
        bins = assign_groups(records, part_count)
        for part in bins:
            part["filename"] = f"{source.stem}_part{part['number']:02d}of{part_count:02d}.zip"
            path = output / part["filename"]
            if path.exists() or Path(str(path) + ".partial").exists():
                raise FileExistsError(f"Refusing to overwrite {path}")
            for record in part["records"]:
                if int(record["bytes"]) != infos[record["archive_path"]].file_size:
                    raise ValueError("Checkpoint size does not match index")
                source_to_part[record["archive_path"]] = part["filename"]
        assignments = [{**record, "part_filename": source_to_part[record["archive_path"]]} for record in records]
        shared = {}
        renames = {"README_ZH.md": "README_FULL_ARCHIVE_ZH.md",
                   "file_manifest.csv": "FULL_ARCHIVE_file_manifest.csv"}
        for name in sorted(set(infos) - set(weight_names)):
            data = original.read(name)
            if name in original_manifest and hashlib.sha256(data).hexdigest() != original_manifest[name]["sha256"]:
                raise ValueError(f"Source member hash mismatch: {name}")
            shared[renames.get(name, name)] = data
        shared["README_ZH.md"] = readme_text(source.name, bins, max_bytes).encode("utf-8")
        shared["part_assignment.csv"] = csv_data(assignments)
        shared_bytes = sum(map(len, shared.values()))
        # Bound against uncompressed size plus generous deflate/header overhead.
        for part in bins:
            upper = int((shared_bytes + part["bytes"]) * 1.002) + (len(shared) + len(part["records"])) * 2048 + 2_000_000
            if upper >= max_bytes:
                raise ValueError(f"Part {part['number']} exceeds conservative size bound: {upper}")
            print(f"PLAN part={part['number']} weights={len(part['records'])} bound_bytes={upper}", flush=True)
        if shutil.disk_usage(output).free < sum(p["bytes"] + shared_bytes for p in bins) + 2**30:
            raise OSError("Insufficient free space")
        (output / "README_ZH.md").write_bytes(shared["README_ZH.md"])
        (output / "part_assignment.csv").write_bytes(shared["part_assignment.csv"])
        expected_hashes = {r["archive_path"]: r["sha256"] for r in records}
        for part in bins:
            number = part["number"]
            destination = output / part["filename"]
            temporary = Path(str(destination) + ".partial")
            manifest = []
            print(f"PART_{number}_WRITE_START", flush=True)
            last_update = time.monotonic()
            with zipfile.ZipFile(temporary, "x", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=1, allowZip64=True) as packed:
                for name, data in shared.items():
                    packed.writestr(name, data)
                    manifest.append(dict(archive_path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
                index_name = f"part{number:02d}_checkpoint_index.csv"
                index_data = csv_data([r for r in assignments if r["part_filename"] == part["filename"]])
                packed.writestr(index_name, index_data)
                manifest.append(dict(archive_path=index_name, bytes=len(index_data), sha256=hashlib.sha256(index_data).hexdigest()))
                for i, record in enumerate(sorted(part["records"], key=lambda r: r["archive_path"]), 1):
                    name = record["archive_path"]
                    digest = hashlib.sha256()
                    count = 0
                    with original.open(name) as src, packed.open(name, "w", force_zip64=True) as dst:
                        while chunk := src.read(CHUNK_SIZE):
                            dst.write(chunk)
                            digest.update(chunk)
                            count += len(chunk)
                    if digest.hexdigest() != expected_hashes[name] or count != int(record["bytes"]):
                        raise ValueError(f"Weight content differs from original index: {name}")
                    manifest.append(dict(archive_path=name, bytes=count, sha256=digest.hexdigest()))
                    if time.monotonic() - last_update >= 20 or i == len(part["records"]):
                        print(f"PART_{number}_WEIGHTS {i}/{len(part['records'])}", flush=True)
                        last_update = time.monotonic()
                manifest_name = f"part{number:02d}_file_manifest.csv"
                manifest_data = csv_data(manifest)
                packed.writestr(manifest_name, manifest_data)
            size = temporary.stat().st_size
            if size >= max_bytes:
                raise ValueError(f"Actual ZIP size exceeds upload limit: {size}")
            print(f"PART_{number}_VERIFY_START bytes={size}", flush=True)
            with zipfile.ZipFile(temporary) as packed:
                names = packed.namelist()
                if len(names) != len(set(names)) or len(names) != len(manifest) + 1:
                    raise ValueError("Duplicate or unexpected archive member")
                if {n for n in names if n.endswith(".pth")} != {r["archive_path"] for r in part["records"]}:
                    raise ValueError("Wrong checkpoint membership")
                for item in manifest:
                    with packed.open(item["archive_path"]) as stream:
                        digest = hashlib.file_digest(stream, "sha256").hexdigest()
                    if digest != item["sha256"]:
                        raise ValueError(f"Readback hash mismatch: {item['archive_path']}")
                if packed.read(manifest_name) != manifest_data:
                    raise ValueError("Manifest readback mismatch")
            temporary.rename(destination)
            archive_hash = digest_file(destination)
            Path(str(destination) + ".sha256").write_text(f"{archive_hash}  {destination.name}\n", encoding="ascii")
            results.append(dict(filename=destination.name, bytes=size, gb=round(size/10**9, 4),
                                checkpoint_count=len(part["records"]), sha256=archive_hash,
                                files_verified=len(manifest) + 1, status="PASS"))
            print(f"PART_{number}_PASS {size / 10**9:.4f} GB", flush=True)
    counts = Counter(r["archive_path"] for part in bins for r in part["records"])
    if set(counts) != set(weight_names) or any(v != 1 for v in counts.values()):
        raise ValueError("Weights are duplicated or missing across ZIPs")
    after = source.stat()
    if (after.st_size, after.st_mtime_ns) != (source_stat.st_size, source_stat.st_mtime_ns):
        raise ValueError("Source archive changed during split")
    report = dict(status="PASS", source_archive=str(source), source_sha256=source_hash,
                  source_preserved=True, max_zip_bytes=max_bytes, independent_zips=True,
                  weight_count=len(counts), table_row_count=len({r['table_row'] for r in records}),
                  missing_weights=[], duplicate_weights=[], all_cv_folds_kept_together=True,
                  all_shared_files_repeated=True, parts=results)
    (output / "split_validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "SHA256SUMS.txt").write_text("".join(f"{p['sha256']}  {p['filename']}\n" for p in results), encoding="ascii")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--parts", type=int, default=4)
    parser.add_argument("--max-bytes", type=int, default=2_000_000_000)
    args = parser.parse_args()
    if args.parts < 1 or args.max_bytes < 1:
        parser.error("parts and max-bytes must be positive")
    split_archive(args.source.resolve(), args.output or args.source.parent / (args.source.stem + "_parts"),
                  args.parts, args.max_bytes)
