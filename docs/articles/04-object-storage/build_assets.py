"""Build publication diagrams (PNG/SVG/Mermaid) and a local article preview.

Requires Pillow, Markdown, and a CJK font set through MYNADB_ARTICLE_FONT.
No network requests are made. Diagram positions are shared by PNG and SVG.
"""
from pathlib import Path
import os, math, html, json
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import markdown

ROOT = Path(__file__).resolve().parent
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
        self.text(40,height-39,'MynaDB · 从零实现系列 04 · 对象存储与查询',15,MUTED)
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
f=Figure('01-storage-abstraction','01 / 用统一接口连接不同存储后端','接口统一访问方式，但各后端的故障与并发语义仍需分别验证。',760)
f.box(360,155,480,95,['写入、查询、WAL、Compaction'],'blue',23)
f.box(360,330,480,105,['Storage：put / get / list / delete','路径前缀与后端配置'],'teal',21)
f.line([(600,250),(600,330)])
f.box(40,540,460,105,['本地文件系统','文件与目录'],'blue',22)
f.box(700,540,460,105,['S3 兼容对象存储','bucket + key + endpoint'],'blue',21)
f.line([(490,435),(270,540)]);f.line([(710,435),(930,540)])
figs.append(f.finish('''flowchart TB
 A[数据库写入与查询] --> B[统一 Storage 接口]
 B --> C[本地文件系统]
 B --> D[S3 兼容对象存储]
'''))

f=Figure('02-write-path','02 / 一批指标如何变成 Parquet 对象','解析字段类型，组织 Arrow 批次，再由存储接口写入后端。',760)
for x,lines,tone in [(40,['Line protocol','解析指标'],'blue'),(330,['Arrow 批次','分片内存缓存'],'blue'),(620,['flush','编码 Parquet'],'teal'),(910,['Storage::put','本地 / 对象'],'teal')]:f.box(x,170,250,115,lines,tone,21)
for x in [290,580,870]:f.line([(x,227),(x+40,227)])
f.box(40,445,520,120,['缓存分片减少锁竞争','周期或容量触发 flush'],'blue',22)
f.box(640,445,520,120,['单个对象写入成功','不等于整批数据原子提交'],'orange',22)
f.box(40,630,1120,65,['确认、提交和恢复边界需要结合实际实现与后端语义验证。'],'gray',21)
figs.append(f.finish('''flowchart LR
 A[Line protocol] --> B[Arrow 批次和分片缓存]
 B --> C[flush 编码 Parquet]
 C --> D[Storage put]
 D --> E[本地或对象存储]
'''))

f=Figure('03-wal-segments','03 / WAL 与对象存储的写入方式','历史版本缓冲一个分段，并持久化完整缓冲；对象并非文件追加。',780)
f.box(40,170,300,115,['WAL 记录','写入内存分段'],'blue',22)
f.box(450,170,300,115,['周期 / 阈值 / 同步策略','触发持久化'],'teal',20)
f.box(860,170,300,115,['完整分段缓冲','put 到对象存储'],'blue',21)
f.line([(340,227),(450,227)]);f.line([(750,227),(860,227)])
f.box(40,450,520,125,['异步：可能存在未持久化窗口','重启恢复依赖已保存状态'],'orange',20)
f.box(640,450,520,125,['完整缓冲反复覆盖','成本及故障语义需要实测'],'gray',21)
f.box(40,655,1120,65,['put 返回与断电持久化不是同一个未经验证的承诺。'],'gray',21)
figs.append(f.finish('''flowchart LR
 A[WAL 记录] --> B[内存分段]
 B --> C[周期或阈值触发]
 C --> D[完整缓冲 put 到存储]
'''))

f=Figure('04-commit-boundary','04 / 上传候选对象不等于提交整批','下图是可讨论的提交方案，不代表 v0.3.0 已实现事务性清单。',820)
for x,lines,tone in [(40,['生成唯一 key','上传候选文件'],'blue'),(330,['验证所有对象','记录候选集合'],'blue'),(620,['条件发布清单','检查前一版本'],'teal'),(910,['查询读取','已提交清单'],'teal')]:f.box(x,160,250,115,lines,tone,20)
for x in [290,580,870]:f.line([(x,218),(x+40,218)])
f.box(40,430,520,130,['上传或发布失败','候选对象不应直接可见','安全回收需要规则'],'orange',20)
f.box(640,430,520,130,['发布成功但响应丢失','用提交标识判断重试','避免重复或遗漏'],'gray',20)
f.box(40,650,1120,70,['多写入者冲突、条件更新与对象可见性依赖实际协议和后端。'],'gray',20)
figs.append(f.finish('''flowchart LR
 A[上传候选对象] --> B[验证对象]
 B --> C[条件发布版本清单]
 C --> D[查询读取已提交集合]
 B -->|失败| E[按规则回收候选对象]
'''))

f=Figure('05-query-cache','05 / 查询中的缓存与数据裁剪','不同缓存解决不同问题：必须同时定义更新与失效边界。',780)
f.box(40,160,260,110,['SQL 查询','时间和列条件'],'blue',21)
f.box(365,160,260,110,['表 / 文件发现','元数据缓存'],'blue',21)
f.box(690,160,220,110,['裁剪','时间 / 列'],'teal',21)
f.box(975,160,185,110,['读取','Parquet'],'teal',21)
for x,y in [(300,365),(625,690),(910,975)]:f.line([(x,215),(y,215)])
f.box(40,430,520,120,['查询结果缓存','写入或文件变化时如何失效？'],'blue',21)
f.box(640,430,520,120,['历史版本查询已持久化文件','内存数据不保证立即可查'],'orange',21)
f.box(40,630,1120,70,['TTL 限制缓存年龄，不能单独保证写后立即可见。'],'gray',21)
figs.append(f.finish('''flowchart LR
 A[SQL] --> B[表和文件元数据]
 B --> C[时间与列裁剪]
 C --> D[读取 Parquet]
 D --> E[查询结果缓存]
'''))

f=Figure('06-compaction','06 / 合并文件还要切换有效集合','图示为安全设计检查项，不代表历史标签已实现事务性合并。',800)
f.box(40,175,300,120,['旧文件集合','小文件 A / B / C'],'blue',22)
f.box(450,175,300,120,['生成并验证','新候选文件 D'],'teal',22)
f.box(860,175,300,120,['发布新文件集合','查询读取新版本'],'teal',21)
f.line([(340,235),(450,235)]);f.line([(750,235),(860,235)])
f.box(40,470,520,120,['失败：旧文件仍可读','清理未提交候选对象'],'orange',21)
f.box(640,470,520,120,['等待旧版本读者完成','再按规则回收旧文件'],'gray',21)
f.box(40,650,1120,65,['避免新旧文件同时计入，或在切换时漏读。'],'gray',21)
figs.append(f.finish('''flowchart LR
 A[旧文件 A B C] --> B[生成候选文件 D]
 B --> C[发布新文件集合]
 C --> D[等待旧读者后回收旧文件]
 B -->|失败| E[保留旧文件并清理候选对象]
'''))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')
body=markdown.markdown((ROOT/'article.md').read_text(),extensions=['tables','fenced_code','toc'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MynaDB 从零实现系列 04：对象存储与查询</title><style>
:root{color-scheme:light}body{margin:0;background:#f3f6fa;color:#233749;font:17px/1.95 system-ui,-apple-system,"Microsoft YaHei",sans-serif}main{max-width:1000px;margin:36px auto;padding:48px 54px;background:white;border:1px solid #e1e8ef;border-radius:16px}h1{font-size:34px;line-height:1.5;letter-spacing:-.6px}h2{font-size:25px;margin-top:48px;padding-top:12px;border-top:1px solid #e2e9ef}a{color:#096d8f}p{margin:20px 0}img{display:block;width:100%;height:auto;margin:28px 0;border:1px solid #e3eaf0;border-radius:10px}pre{padding:22px;background:#112b3c;color:#e2edf5;overflow:auto;border-radius:10px;font:14px/1.8 ui-monospace,monospace}code{font-family:ui-monospace,monospace;font-size:.9em}p code,td code,li code{background:#eef3f8;padding:2px 5px;border-radius:4px}table{border-collapse:collapse;width:100%;font-size:15px;margin:24px 0}td,th{border:1px solid #dce5ed;padding:12px;text-align:left}th{background:#edf5f9}li{margin:8px 0}strong{color:#123c52}.draft{font-size:14px;color:#617a8d;border-bottom:1px solid #e0e8ef;padding-bottom:15px}@media(max-width:700px){main{margin:0;padding:24px 18px;border:0;border-radius:0}h1{font-size:27px}table{display:block;overflow:auto}pre{padding:15px}}
</style><main><p class="draft">社区文章草稿 · 对象存储与查询 · 本地预览，尚未对外发表</p>'''+body+'</main></html>'
(ROOT/'preview.html').write_text(page)
print('Generated',len(figs),'PNG/SVG/Mermaid figures and preview.html')
