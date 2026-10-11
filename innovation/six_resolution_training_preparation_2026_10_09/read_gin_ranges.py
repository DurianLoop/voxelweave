"""Print bounded saved GIN author-text ranges; record transport scope separately from final read audit."""
import sys,json,gzip
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
resource_guard();start,end=map(int,sys.argv[1:3]);source=HERE/'gin_primary_html_attempt02/blocks.json.gz'
blocks=json.loads(gzip.decompress(source.read_bytes()));assert 0<=start<end<=len(blocks)
for b in blocks[start:end]:print(str(b['index'])+' ['+b['tag']+'] '+b['text'])
out=HERE/'gin_reading_ranges_attempt01';out.mkdir(exist_ok=True)
dump(out/f'range_{start:03}_{end:03}.json',dict(complete=True,range_start=start,range_end_exclusive=end,
 blocks_printed=end-start,extracted_source=entry(source),printing_not_independent_read_confirmation=True,
 actual_reading_scope_to_be_finalized_after_tool_output_inspection=True))
