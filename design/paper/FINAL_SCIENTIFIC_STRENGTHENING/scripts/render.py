from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];CV=P/'revised_manuscript'
OUT=P/'final_page_renders_v2';OUT.mkdir(exist_ok=True)
for name,stem in [('cvpr','main'),('supplement','supplement')]:
    subprocess.run(['pdftoppm','-r','95','-png',str(CV/(stem+'.pdf')),str(OUT/name)],check=True,capture_output=True)
    files=sorted(OUT.glob(name+'-*.png'))
    for start in range(0,len(files),6):
        group=files[start:start+6];sheet=Image.new('RGB',(1200,570*((len(group)+2)//3)),'#DDDDDD');draw=ImageDraw.Draw(sheet)
        for k,p in enumerate(group):
            im=Image.open(p).convert('RGB');im.thumbnail((385,540));x=k%3*400+(400-im.width)//2;y=k//3*570+25
            sheet.paste(im,(x,y));draw.text((x,y-20),p.name,fill='black')
        sheet.save(OUT/f'{name}_contact_{start//6+1}.png')
    print(name,len(files),'pages rendered',flush=True)
