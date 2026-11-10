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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 08 · 表所有权与分区路由',15,MUTED)
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
f=Figure('01-two-levels','01 / 表所有权与物理文件是两层信息','表级元数据与物理路径服务不同的路由问题。',740)
f.box(40,170,330,135,['Meta 控制面', '表与 owner 列表'],'blue',20)
f.box(435,170,330,135,['逻辑表', 'catalog / schema / table'],'teal',20)
f.box(830,170,330,135,['对象存储', 'date / node_id / 文件'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['物理路径中的节点标识不等于当前唯一写入 owner。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[Meta 控制面] --> B[逻辑表]\n  C[对象存储] --> B\n  N[物理路径中的节点标识不等于当前唯一写入 owner。]'))
f=Figure('02-table-owners','02 / 一张表可能有多个 owner','故障重路由或数据分布后，查询应考虑所有相关数据。',740)
f.box(40,170,330,135,['写入请求', '定位逻辑表'],'blue',20)
f.box(435,170,330,135,['表 owner 列表', '带活动状态和 TTL'],'teal',20)
f.box(830,170,330,135,['多个节点', '新数据与历史分布'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['TTL 清理不单独等于写入隔离或 fencing。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[写入请求] --> B[表 owner 列表]\n  B --> C[多个节点]\n  N[TTL 清理不单独等于写入隔离或 fencing。]'))
f=Figure('03-hive-layout','03 / 按日期和节点组织物理文件','可从日期前缀发现 node_id 子路径。',740)
f.box(40,170,330,135,['逻辑表', 'catalog / schema / table'],'blue',20)
f.box(435,170,330,135,['日期前缀', 'date=2026-02-01'],'teal',20)
f.box(830,170,330,135,['物理节点分区', 'node_id=data-1'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['路径布局变化需要明确迁移与回滚，不能假定自动兼容。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[逻辑表] --> B[日期前缀]\n  B --> C[物理节点分区]\n  N[路径布局变化需要明确迁移与回滚，不能假定自动兼容。]'))
f=Figure('04-hot-cold','04 / 查询需要同时考虑内存和文件','近期数据可能仍在内存，文件可通过存储前缀发现。',740)
f.box(40,170,330,135,['候选 owner', '可能含内存数据'],'blue',20)
f.box(435,170,330,135,['查询路由', '结合范围与缓存'],'teal',20)
f.box(830,170,330,135,['存储发现', '已持久化分区'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['旧日期迟到数据仍在内存时，必须测试是否被正确发现。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[候选 owner] --> B[查询路由]\n  C[存储发现] --> B\n  N[旧日期迟到数据仍在内存时，必须测试是否被正确发现。]'))
f=Figure('05-affinity-fallback','05 / 本地亲和与节点不可用时回退','分区标识、执行节点与表 owner 不一定相同。',740)
f.box(40,170,330,135,['发现物理分区', 'node_id=data-1'],'blue',20)
f.box(435,170,330,135,['优先原节点', '复用本地缓存'],'teal',20)
f.box(830,170,330,135,['节点不可用', '回退到可用节点'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['回退时保留原分区范围，避免遗漏或重复读取。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[发现物理分区] --> B[优先原节点]\n  B --> C[节点不可用]\n  N[回退时保留原分区范围，避免遗漏或重复读取。]'))
f=Figure('06-routing-tests','06 / 通过结果验证路由','使用有稳定标识的数据，与不裁剪的可信结果比较。',740)
f.box(40,170,330,135,['多 owner / 迟到数据', '验证完整性'],'blue',20)
f.box(435,170,330,135,['节点故障 / 文件变化', '验证回退与失效'],'teal',20)
f.box(830,170,330,135,['聚合 / 日期边界', '验证 SQL 语义'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['这些是建议的测试场景，不是已执行的结果。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[多 owner / 迟到数据] --> B[节点故障 / 文件变化]\n  B --> C[聚合 / 日期边界]\n  N[这些是建议的测试场景，不是已执行的结果。]'))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
