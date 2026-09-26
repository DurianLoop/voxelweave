from pathlib import Path
import subprocess, json
from PIL import Image, ImageOps, ImageDraw
P13=Path(__file__).resolve().parents[1]; PAPER=P13.parent
OUT=P13/'final_page_renders_verified'; OUT.mkdir(exist_ok=True)
jobs={'tmi_baselines':PAPER/'TMI/TMI_ARCH_GENERALIZED/baseline_supplement.pdf','cvpr':PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf','supplement':PAPER/'CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf','tmi':PAPER/'TMI/TMI_ARCH_GENERALIZED/main.pdf'}
jobs={k:v for k,v in jobs.items() if k in {'cvpr','tmi'}}
for name,pdf in jobs.items():
    subprocess.run(['pdftoppm','-r','95','-png',str(pdf),str(OUT/name)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    files=sorted(OUT.glob(name+'-*.png'))
    for start in range(0,len(files),6):
        group=files[start:start+6]; sheet=Image.new('RGB',(1200,570*((len(group)+2)//3)),'#DDDDDD'); draw=ImageDraw.Draw(sheet)
        for k,p in enumerate(group):
            im=Image.open(p).convert('RGB'); im.thumbnail((385,540))
            x=(k%3)*400+(400-im.width)//2; y=(k//3)*570+25
            sheet.paste(im,(x,y)); draw.text((x,y-20),p.name,fill='black')
        sheet.save(OUT/f'{name}_contact_{start//6+1}.png')
    print(name,len(files),'pages rendered',flush=True)
