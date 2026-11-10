"""Build publication diagrams (PNG/SVG/Mermaid) and a local article preview.

Requires Pillow, Markdown, and a CJK font set through MYNADB_ARTICLE_FONT.
No network requests are made. Diagram positions are shared by PNG and SVG.
"""
from pathlib import Path
import sys
import os, math, html, json
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from publish_support import export_article
from site_support import render_article, render_index
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
FONT = Path(os.environ.get('MYNADB_ARTICLE_FONT', str(ROOT / 'NotoSansSC.ttf')))
if not FONT.is_file():
    raise SystemExit('Set MYNADB_ARTICLE_FONT to a Chinese TrueType/OpenType font.')
SCALE = 2
INK = '#18364a'; MUTED = '#536a7b'; LINE = '#718698'
PALETTE = {'blue': ('#edf5ff','#80acd8'), 'teal': ('#e9f7f3','#75b6a7'),
           'gray': ('#f3f5f8','#bdcbd5'), 'orange': ('#fff4e8','#e1a76a')}

class Figure:
    def __init__(self, name, title, subtitle, height=760):
        self.name=name; self.w=1200; self.h=height; self.title=title
        self.im=Image.new('RGB',(self.w*SCALE,self.h*SCALE),'white')
        self.d=ImageDraw.Draw(self.im)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
          f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>',
          '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#718698"/></marker></defs>',
          '<rect width="100%" height="100%" fill="white"/>']
        self.text(40,30,title,30)
        self.text(40,79,subtitle,17,MUTED)
        self.line([(40,116),(1160,116)],False)
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 05 · Memtable 与查询',15,MUTED)
    @lru_cache(maxsize=24)
    def font(self,size):
        font=ImageFont.truetype(str(FONT),size*SCALE)
        try:
            axes=font.get_variation_axes()
            font.set_variation_by_axes([500 if axis['name']==b'Weight' else axis['default'] for axis in axes])
        except (AttributeError,OSError):
            pass
        return font
    def text(self,x,y,s,size=21,color=INK):
        f=self.font(size)
        self.d.text((int(x*SCALE),int(y*SCALE)),s,font=f,fill=color,anchor='lt')
        self.svg.append(f'<text x="{x}" y="{y+size}" font-family="Noto Sans SC, Microsoft YaHei, PingFang SC, sans-serif" font-size="{size}" font-weight="500" fill="{color}">{html.escape(s)}</text>')
    def box(self,x,y,w,h,lines,tone='blue',size=21):
        fill,stroke=PALETTE[tone]
        self.d.rounded_rectangle(tuple(int(v*SCALE) for v in (x,y,x+w,y+h)),radius=13*SCALE,fill=fill,outline=stroke,width=2*SCALE)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="13" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        if isinstance(lines,str):lines=lines.split('\n')
        lh=size+12; top=y+(h-len(lines)*lh)/2+3
        for i,s in enumerate(lines):
            width=self.d.textlength(s,font=self.font(size))/SCALE
            if width>w-26:raise ValueError(f'{self.name}: label too wide: {s}')
            self.text(round(x+(w-width)/2,1),round(top+i*lh,1),s,size)
    def line(self,points,arrow=True,dashed=False):
        pp=[(int(x*SCALE),int(y*SCALE)) for x,y in points]
        if dashed:
            for a,b in zip(pp,pp[1:]):
                dist=math.dist(a,b)
                for j in range(0,int(dist),18*SCALE):
                    u=j/dist;v=min((j+9*SCALE)/dist,1)
                    self.d.line([(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u),(a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v)],fill=LINE,width=2*SCALE)
        else:self.d.line(pp,fill=LINE,width=2*SCALE,joint='curve')
        if arrow:
            ax,ay=pp[-2];bx,by=pp[-1];ang=math.atan2(by-ay,bx-ax)
            tip=[(bx,by)]+[(bx-11*SCALE*math.cos(ang+off),by-11*SCALE*math.sin(ang+off)) for off in (-.45,.45)]
            self.d.polygon(tip,fill=LINE)
        path=' '.join(f'{x},{y}' for x,y in points)
        self.svg.append(f'<polyline points="{path}" fill="none" stroke="{LINE}" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="9 9"' if dashed else '')+'/>')
    def finish(self,mermaid):
        self.svg.append('</svg>')
        (OUT/(self.name+'.svg')).write_text('\n'.join(self.svg)+'\n')
        self.im.save(OUT/(self.name+'.png'),optimize=True)
        (OUT/(self.name+'.mmd')).write_text(mermaid.strip()+'\n')
        return {'name':self.name,'title':self.title,'width':self.w*SCALE,'height':self.h*SCALE}

figs=[]
f=Figure('01-two-sources','05 / 一张逻辑表的两个数据来源','查询可组合内存中的新写入与已持久化 Parquet。',740)
f.box(40,170,330,135,['新写入', '内存 RecordBatch'],'blue',20)
f.box(435,170,330,135,['统一表', '两种数据来源'],'teal',20)
f.box(830,170,330,135,['已 flush', 'Parquet 文件'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['可见性与持久化是不同承诺。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[新写入] --> B[统一表]\n  C[已 flush] --> B\n  N[可见性与持久化是不同承诺。]'))
f=Figure('02-providers','05 / 从 SQL 到两个扫描计划','TableProvider 为 DataFusion 提供 schema 和扫描路径。',740)
f.box(40,170,330,135,['SQL', 'DataFusion'],'blue',20)
f.box(435,170,330,135,['Union Provider', '统一查询入口'],'teal',20)
f.box(830,170,330,135,['Memtable / Parquet', '各自执行扫描'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['合并结果需要正确处理 schema、过滤与重复。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[SQL] --> B[Union Provider]\n  B --> C[Memtable / Parquet]\n  N[合并结果需要正确处理 schema、过滤与重复。]'))
f=Figure('03-flush-visibility','05 / flush 期间如何避免漏读和重复','示意设计：查询应读取相互一致的内存与文件版本。',740)
f.box(40,170,330,135,['版本一', '内存持有批次 A'],'blue',20)
f.box(435,170,330,135,['写入并发布文件', '切换可见版本'],'teal',20)
f.box(830,170,330,135,['版本二', '文件持有批次 A'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['这是设计目标；不是对历史版本事务快照的承诺。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[版本一] --> B[写入并发布文件]\n  B --> C[版本二]\n  N[这是设计目标；不是对历史版本事务快照的承诺。]'))
f=Figure('04-schema-alignment','05 / 按列名对齐，而不是按位置拼接','两个来源的列集合、顺序和类型可能不同。',740)
f.box(40,170,330,135,['内存', 'time / host / usage / temp'],'blue',20)
f.box(435,170,330,135,['统一 schema', '按列名映射'],'teal',20)
f.box(830,170,330,135,['Parquet', 'time / host / usage'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['缺失列补空值；类型冲突和投影需要明确处理。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[内存] --> B[统一 schema]\n  B --> C[Parquet]\n  N[缺失列补空值；类型冲突和投影需要明确处理。]'))
f=Figure('05-pruning','05 / 尽早缩小需要读取的数据','裁剪是优化，不能改变 SQL 的最终结果。',740)
f.box(40,170,330,135,['时间过滤', '筛选相关分区'],'blue',20)
f.box(435,170,330,135,['Parquet 统计', '跳过无关数据'],'teal',20)
f.box(830,170,330,135,['列投影', '读取需要的列'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['无法安全判断时保守读取；非精确过滤需再次检查。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[时间过滤] --> B[Parquet 统计]\n  B --> C[列投影]\n  N[无法安全判断时保守读取；非精确过滤需再次检查。]'))
f=Figure('06-cache-invalidation','05 / 数据变化后如何处理缓存','写入、flush、compaction 和 schema 变化都可能影响结果。',740)
f.box(40,170,330,135,['数据发生变化', '标记受影响表'],'blue',20)
f.box(435,170,330,135,['元数据 / 结果缓存', '失效或更新版本'],'teal',20)
f.box(830,170,330,135,['并发查询', '避免旧结果重新生效'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['TTL 不能单独保证写后立即可见。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[数据发生变化] --> B[元数据 / 结果缓存]\n  B --> C[并发查询]\n  N[TTL 不能单独保证写后立即可见。]'))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
