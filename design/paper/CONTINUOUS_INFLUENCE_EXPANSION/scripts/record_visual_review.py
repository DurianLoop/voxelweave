from adapters import *
import datetime

assert (P/'VISUAL_REVIEW.md').exists()
verified=read(P/'outputs/manuscript_verification.json')
assert verified['status']=='PASS'
hashes={s:sha(P/'revised_manuscript'/f'{s}.pdf') for s in ['main','supplement']}
assert hashes==verified['pdf_sha256']
write(P/'outputs/visual_review.json',dict(
    status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    pdf_sha256=hashes,main_pages_reviewed=list(range(1,10)),
    supplement_pages_reviewed=list(range(1,42)),
    individual_page_review=['main-7.png','supplement-39.png'],
    method='All-page rendered contact sheets plus individual critical pages; inspected by assistant',
    notes='VISUAL_REVIEW.md'))
print('Visual inspection recorded for verified final PDFs')
