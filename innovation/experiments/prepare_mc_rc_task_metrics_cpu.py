"""Extract existing metric implementations without importing either Torch support."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    target = ROOT / 'experiments/mc_rc_task_metrics_cpu.py'
    proof = ROOT / 'experiments/mc_rc_task_metrics_cpu_sources.json'
    assert not target.exists() and not proof.exists()
    requested = {
        'mc_rc_sparse_task_cpu_pilot_support.py': ['counts', 'surface_metrics', 'metrics'],
        'verify_mc_rc_sparse_task_training_cpu_pilot.py':
            ['independent_label', 'independent_counts', 'surface_points', 'independent_surface'],
    }
    header = '''"""Existing metric algorithms extracted without Torch; sources recorded beside this file."""
import numpy as np
import nibabel as nib
from scipy.ndimage import binary_erosion, distance_transform_edt, generate_binary_structure
from scipy.spatial import cKDTree
from mc_rc_observed_only_training_input import ROOT, sha, support_domains
'''
    blocks, bindings = [], []
    for filename, names in requested.items():
        source = ROOT / 'experiments' / filename
        content = source.read_text(encoding='utf-8')
        nodes = {n.name: n for n in ast.parse(content).body if isinstance(n, ast.FunctionDef)}
        for name in names:
            segment = ast.get_source_segment(content, nodes[name])
            blocks.append(segment)
            bindings.append(dict(source=source.relative_to(ROOT).as_posix(),
                                 source_sha256=sha(source), function=name,
                                 extracted_utf8_sha256=hashlib.sha256(segment.encode()).hexdigest()))
    target.write_text(header + '\n\n' + '\n\n'.join(blocks) + '\n', encoding='utf-8')
    proof.write_text(json.dumps(dict(generator_sha256=sha(__file__),
                                    output_sha256=sha(target), functions=bindings,
                                    algorithms_reused=True, torch_imported=False),
                                ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(functions=len(bindings), output_sha256=sha(target))))


if __name__ == '__main__':
    main()
