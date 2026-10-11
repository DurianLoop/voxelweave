"""V2 supports the original geometry-refinement receipt without altering the failed V1."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
ORIGINAL=HERE/'audit_allowed_label_timepoints.py'
source=ORIGINAL.read_text(encoding='utf-8')
old="""            if str(resultpath) not in cache:
                q=read(resultpath);cache[str(resultpath)]=[s for s in q['series'] if s.get('series_uid') in allowed]
            s=next(s for s in cache[str(resultpath)] if s['series_uid']==uid)
"""
new="""            if str(resultpath) not in cache:
                q=read(resultpath)
                if resultpath.name=='geometry_availability_attempt_01.json':
                    labels=ROOT/'experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json'
                    assert sha(labels)==q['first_label_grid_attempt_sha256'];sources.append(labels)
                    labelrows={x['series_uid']:x for x in read(labels)['series'] if x.get('series_uid') in allowed}
                    cache[str(resultpath)]=[dict(labelrows[x['uid']],grid=x['grid_with_fitted_affine'])
                        for x in q['series'] if x.get('uid') in allowed]
                else:cache[str(resultpath)]=[x for x in q['series'] if x.get('series_uid') in allowed]
            s=next(x for x in cache[str(resultpath)] if x['series_uid']==uid)
"""
assert source.count(old)==1
source=source.replace(old,new)
source=source.replace("'ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT.json'","'ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT_V2.json'")
source=source.replace("sources=[Path(__file__)]","sources=[Path(__file__),HERE/'audit_allowed_label_timepoints.py',HERE/'ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT.json']")
if __name__=='__main__':exec(compile(source,str(ORIGINAL),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
