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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 10 · 正确性与互操作',15,MUTED)
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
f=Figure('01-compaction-overlap','01 / 合并输出与旧文件重叠','旧文件删除失败时，查询不能简单读取所有文件。',740)
f.box(40,170,330,135,['旧文件 A / B / C', '参与合并'],'blue',20)
f.box(435,170,330,135,['输出文件 D', '包含合并数据'],'teal',20)
f.box(830,170,330,135,['Compaction 清单', '排除被替代文件'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['历史清单读取失败退回空集合；故障窗口仍需验证。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[旧文件 A / B / C] --> B[输出文件 D]\n  B --> C[Compaction 清单]\n  N[历史清单读取失败退回空集合；故障窗口仍需验证。]'))
f=Figure('02-schema-alignment','02 / 按字段名对齐异构数据','内存和文件可能缺列、重排或使用不同编码。',740)
f.box(40,170,330,135,['内存批次', 'time / host / usage / temp'],'blue',20)
f.box(435,170,330,135,['统一 schema', '按名称匹配'],'teal',20)
f.box(830,170,330,135,['Parquet', 'time / usage / host'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['缺列补 null；类型冲突和空投影需要分别测试。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[内存批次] --> B[统一 schema]\n  C[Parquet] --> B\n  N[缺列补 null；类型冲突和空投影需要分别测试。]'))
f=Figure('03-distributed-aggregation','03 / 局部结果到全局结果','全局 AVG 应正确合并 sum 和 count。',740)
f.box(40,170,330,135,['节点 A', 'sum = 100 / count = 10'],'blue',20)
f.box(435,170,330,135,['全局汇总', 'sum = 190 / count = 11'],'teal',20)
f.box(830,170,330,135,['节点 B', 'sum = 90 / count = 1'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['不能对各节点的平均值直接再次求平均。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[节点 A] --> B[全局汇总]\n  C[节点 B] --> B\n  N[不能对各节点的平均值直接再次求平均。]'))
f=Figure('04-otlp','04 / OTLP 消息如何进入写入路径','metrics、logs 和 traces 分别映射为内部数据点。',740)
f.box(40,170,330,135,['OTLP HTTP / gRPC', '遥测消息'],'blue',20)
f.box(435,170,330,135,['转换器', '字段 / 属性 / 时间'],'teal',20)
f.box(830,170,330,135,['内部 Point', '进入写入路径'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['具体客户端、信号类型和部署角色需单独验证。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[OTLP HTTP / gRPC] --> B[转换器]\n  B --> C[内部 Point]\n  N[具体客户端、信号类型和部署角色需单独验证。]'))
f=Figure('05-iceberg','05 / Iceberg 初版与 Parquet 文件','表元数据和清单的格式决定外部引擎能否互通。',740)
f.box(40,170,330,135,['表元数据', 'schema / snapshot'],'blue',20)
f.box(435,170,330,135,['Iceberg manifest', '追踪数据文件'],'teal',20)
f.box(830,170,330,135,['Parquet', '存储数据'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['v0.9.0 初版清单为 JSON，未认证与外部引擎互通。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[表元数据] --> B[Iceberg manifest]\n  B --> C[Parquet]\n  N[v0.9.0 初版清单为 JSON，未认证与外部引擎互通。]'))
f=Figure('06-correctness-tests','06 / 从错误案例到可复现验证','用稳定输入和可信结果检查查询与恢复。',740)
f.box(40,170,330,135,['合并 / 异构 schema', '遗漏与重复'],'blue',20)
f.box(435,170,330,135,['分布式聚合 / 缓存', '全局结果与失效'],'teal',20)
f.box(830,170,330,135,['OTLP / Iceberg', '真实客户端兼容'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['这些是建议的测试场景，不是已执行的结果。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[合并 / 异构 schema] --> B[分布式聚合 / 缓存]\n  B --> C[OTLP / Iceberg]\n  N[这些是建议的测试场景，不是已执行的结果。]'))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
