"""Record actual inherited reading scope and source identity; not another reading execution."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;SRC=HERE/'adaptation_sources_attempt01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def indices(*items):
    result=[]
    for item in items:result.extend(range(item[0],item[1]+1) if isinstance(item,tuple) else [item])
    return sorted(set(result))
def record(identity,filename,scope,kind):
    p=SRC/filename;b=json.loads(p.read_text(encoding='utf-8'));assert all(i<len(b) for i in scope)
    return dict(identity=identity,source_blocks_file=p.relative_to(ROOT).as_posix(),source_sha256=sha(p),
                available_extracted_blocks=len(b),actually_read_indices=scope,reading_kind=kind,
                actual_visual_figures_reviewed=0,author_code_executed=False,pretrained_weights_downloaded=False,
                evidence_basis='Received handoff plus recovered turn16 tool records; acquisition/extraction alone is not counted as reading')
def main():
    records=[
      record(dict(title='Models Genesis',DOI='10.1016/j.media.2020.101840',PMCID='PMC7726094'),
        'genesis2021_bioc_blocks.json',indices(0,1,14,16,17,20,22,24,25,30,32,34,(37,40),42,44,46,48,50,52,
          (54,56),60,61,(63,67),(69,71),73,74,76,77,80,82,83,(85,88),90,108,136,142,147,148,151,153,(155,157),(221,238)),
        'Focused methods/results/discussion/appendix and primary table text; not all 247 blocks'),
      record(dict(title='Head and Neck Tumor Segmentation for MRI-Guided Radiation Therapy Using Pre-trained STU-Net Models',
        DOI='10.1007/978-3-031-83274-1_4',PMCID='PMC11983000'),
        'stu_mri2025_jats_blocks.json',indices((0,65)),'All extracted text including references and duplicate captions'),
      record(dict(title='STU-Net: Scalable and Transferable Medical Image Segmentation Models Empowered by Large-Scale Supervised Pre-training',arxiv='2304.06716v1'),
        'stu_original_arxiv_blocks_v2.json',indices((22,43),48,(50,52),(54,74),(81,84),141,142,158,159),
        'Focused architecture/training/evaluation/limitations and table text; not all 160 blocks'),
      record(dict(title='Colormap augmentation: a novel method for cross-modality domain generalization',DOI='10.1007/s11548-025-03559-y',PMCID='PMC13035743'),
        'colormap_jats_blocks.json',indices((0,60)),
        'Main text/methods/results/tables/discussion complete; relevant BigAug reference checked separately, remaining references not fully read')]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],new_distinct_papers_with_primary_text_read=4,
        all_four_papers_full_scope_read=False,papers=records,
        secondary_reference_checked=dict(paper='Colormap augmentation',ref='13',linked_DOI='10.1109/TMI.2020.2973595'),
        not_counted_as_primary_read=[dict(title='Generalizing deep learning for medical image segmentation to unseen domains via deep stacked transformation',
          DOI='10.1109/TMI.2020.2973595',PMCID='PMC7393676',reason='Full-text HTTP429, empty extraction'),
          dict(PMCID='PMC11111906',reason='MC-RC author paper reread, previously counted')],
        acquisition_failures_preserved=True,figure_pixels_read=False,PDF_files_added=0,
        tool_record_limitations=['Static AST verification return reconstructed from observed e4c30f result after one failed store(undefined); not a new execution',
          'colormap_template_cleanup_read stored scope only; actual 322eac full tool object not preserved, handoff records successful read of blocks13–26'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in
          [Path(__file__),HERE/'ADAPTATION_PAPER_NOTES.md',HERE/'RECOVERED_TURN16_TOOL_RECORDS.json']])
    with (HERE/'READING_PROVENANCE.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,new_distinct_primary_text_papers=4,actual_visual_figures=0)))
if __name__=='__main__':main()
