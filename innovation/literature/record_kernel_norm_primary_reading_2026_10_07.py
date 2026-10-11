"""Append actual KNConv reading and visual review without rewriting acquisition/old reading records."""
import hashlib, json, re, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'literature/source_cache/kernel_normalization_visual_review_2026-10-07'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = OUT/'actual_reading_and_visual_review_attempt01.json'; assert not path.exists()
    rendered = read(OUT/'render_attempt01.json')
    pdf = ROOT/rendered['source_pdf']; assert sha(pdf) == rendered['source_pdf_sha256']
    assert re.search(r'^Pages:\s+21\s*$', (OUT/'pdfinfo.txt').read_text(encoding='utf-8'), re.M)
    pages = ROOT/'literature/source_cache/kernel_normalization_primary_2026-10-07/kernel_norm_pages.json'
    assert [p['page'] for p in read(pages)] == list(range(1, 22))
    notes = {
        4: 'Eq1-3: dropout statistics normalize original window; population variance across all channels and padded local pixels.',
        6: 'Eq5 and Algorithm1: output subtraction and inverse standard deviation before bias; paper uses unfold and var_mean.',
        12: 'Normalization/dropout ablation is CIFAR100; primitive BN vs CUDA BN runtime fairness is explicit.',
        21: 'Tables6-8: actual hardware/batch units checked; KNResNet50 13.6GB vs BN CUDA5.7GB and primitive8.2GB; not local 3D memory qualification.'}
    visuals = []
    for row in rendered['rendered']:
        assert row['physical_page'] in notes and sha(ROOT/row['image']) == row['sha256']
        visuals.append(dict(**row, actual_visual_review=True, note=notes[row['physical_page']]))
    report = ROOT/'literature/2026-10-07_kernel_norm_primary_reading_and_numerical_preparation.md'
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], script_sha256=sha(__file__),
        newly_completed_primary_papers=1, version='arXiv2205.10089v4', physical_pdf_pages=21,
        physical_pages_textually_read=list(range(1, 22)), text_reading_inherited_from_user_handoff=list(range(2, 14))+[19, 20, 21],
        unique_completion_pages_read_in_current_continuation=[1, 14, 15, 16, 17, 18], current_pages_rechecked=[5, 6, 13],
        physical_pages_visually_read=[4, 6, 12, 21], all_other_figure_pixels_not_reviewed=True,
        source_pdf=pdf.relative_to(ROOT).as_posix(), source_pdf_sha256=sha(pdf),
        extracted_pages=pages.relative_to(ROOT).as_posix(), extracted_pages_sha256=sha(pages), visual_reviews=visuals,
        report=report.relative_to(ROOT).as_posix(), report_sha256=sha(report),
        acquisition_and_three_paper_reading_records_preserved=True, author_experiments_reproduced=False,
        original_float32_failure_retained=True, centered_prototype_known_operator=True, publication_claim_confirmed=False)
    with path.open('x', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    failure = ROOT/'experiments/mc_rc_3d_local_kernel_normalization_centered_bootstrap_failure_2026_10_07.json'
    observation = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        record_kind='observed_tool_failure_before_main', observed_tool_exit=1,
        failed_command='python innovation/experiments/qualify_mc_rc_3d_local_kernel_normalization_centered_2026_10_07.py',
        default_interpreter='D:/conda/python.exe', error="ModuleNotFoundError: No module named 'nibabel'",
        failure_phase='import_before_main', actual_training_updates=0, actual_gpu_updates=0,
        recovery_interpreter='D:/conda/envs/MRI/python.exe -X utf8 -B', recovery_observed_tool_exit=0,
        recovery_result='experiments/mc_rc_3d_local_kernel_normalization_centered_2026_10_07/attempt01.json',
        root_environment_modified=False, additional_text_output_failure='GBK UnicodeEncodeError; recovered with stdout UTF8 reconfiguration',
        author_or_scientific_failure=False)
    with failure.open('x', encoding='utf-8') as f: json.dump(observation, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(dict(complete=True, newly_completed_primary_papers=1, cumulative_textual_pages=21, visually_read_pages=4)))
if __name__ == '__main__': main()
