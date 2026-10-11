"""Line counts or prespecified keyword excerpts, never executes downloaded source."""
import sys,gzip,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
if sys.argv[1]=='counts':
    for folder in ['public_sources_attempt02','amdu_blobs_attempt01']:
        for p in sorted((HERE/folder).glob('*.txt.gz')):
            lines=gzip.decompress(p.read_bytes()).decode('utf-8').splitlines();print(str(p.relative_to(HERE))+' '+str(len(lines)))
else:
    p=(HERE/sys.argv[2]).resolve();assert p.is_relative_to(HERE)
    lines=gzip.decompress(p.read_bytes()).decode('utf-8').splitlines();pattern=re.compile(sys.argv[3],re.I);radius=int(sys.argv[4]);indices=set()
    for i,line in enumerate(lines):
        if pattern.search(line):indices.update(range(max(0,i-radius),min(len(lines),i+radius+1)))
    for i in sorted(indices):print(str(i+1)+': '+lines[i])
