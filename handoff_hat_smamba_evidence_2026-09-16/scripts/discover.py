from pathlib import Path
import subprocess, json, csv, re, zipfile

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
roots = [ROOT, Path('C:/Users/user/Documents'), Path('C:/Users/user/Desktop'), Path('C:/Users/user/Downloads'), Path('D:/BaiduNetdiskDownload'), Path('D:/BaiduNetdisk/download'), Path('D:/SAM'), Path('D:/xwechat_files')]
records, matches, archives, required = [], [], [], []
for root in roots:
    p = subprocess.run(['rg', '--files', '--hidden', '--no-ignore', '-g', '!.git/**', str(root)], capture_output=True, encoding='utf-8', errors='replace')
    paths = p.stdout.splitlines()
    relevant=[]
    for s in paths:
        if str(OUT).lower() in s.lower(): continue
        q=Path(s); low=s.lower(); name=q.name.lower()
        if name in ['handofff.md','协议.md','结果.md','agents.md'] or 'baseline_exposed_problems_for_model_design' in name:
            required.append(s)
        if ('hat' in low or 'smamba' in low or 'mamba' in low) and q.suffix.lower() in ['.csv','.json','.pt','.pth','.md','.log','.py','.ps1','.yaml','.yml']:
            if root == ROOT or re.search(r'(?:ixi|ningxia|fastmri|transfer_package|t2x4|smamba|hat_2p5d)', low): relevant.append(s)
        if 'best_strict_val_x4.pt' == name or name in ['strict_summary_compact.csv','strict_val_history.csv']:
            relevant.append(s)
        if q.suffix.lower() in ['.zip','.7z','.rar','.tar'] and re.search(r'mri|t2x4|transfer_package|baseline|hat|smamba|handoff',name): archives.append(s)
    matches.extend(relevant)
    records.append({'root':str(root),'listed_files':len(paths),'relevant_candidates':len(relevant),'returncode':p.returncode,'errors':p.stderr.strip()})
    print(str(root),len(paths),len(relevant), 'errors:',p.stderr[:200],flush=True)
(OUT/'search_scope.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'search_candidates.txt').write_text('\n'.join(sorted(set(matches))),encoding='utf-8')
(OUT/'required_document_search.txt').write_text('\n'.join(sorted(set(required))),encoding='utf-8')
(OUT/'archive_candidates.txt').write_text('\n'.join(sorted(set(archives))),encoding='utf-8')
print('Required documents:', required)
print('Archives:', archives)
