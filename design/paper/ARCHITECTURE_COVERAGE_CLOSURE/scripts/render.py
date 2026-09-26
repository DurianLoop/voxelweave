from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];OUT=P/'page_renders/final';OUT.mkdir(parents=True,exist_ok=True)
for stem in ['main','supplement']:
 subprocess.run(['pdftoppm','-r','90','-png',str(P/'revised_manuscript'/f'{stem}.pdf'),str(OUT/stem)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 pages=sorted(OUT.glob(stem+'-*.png'))
 for start in range(0,len(pages),9):
  subset=pages[start:start+9];canvas=Image.new('RGB',(1950,870*((len(subset)+2)//3)),'#dddddd');draw=ImageDraw.Draw(canvas)
  for j,f in enumerate(subset):
   im=Image.open(f).convert('RGB');im.thumbnail((630,835));x=(j%3)*650+10;y=(j//3)*870+25;canvas.paste(im,(x,y));draw.text((x,y-20),f.name,fill='black')
  canvas.save(OUT/f'{stem}_contact_{start//9+1}.jpg',quality=90)
 print(stem,len(pages),'pages rendered',flush=True)
