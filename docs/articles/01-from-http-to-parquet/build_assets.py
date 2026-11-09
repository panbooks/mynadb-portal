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
        self.text(40,height-39,'MynaDB · 从零实现系列 01 · 单机基础设计',15,MUTED)
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
f=Figure('01-architecture','01 / 第一阶段：单机读写闭环','写入先缓冲再落盘；第一版先实现文件数据的 SQL 查询。',780)
for x,lines,tone in [(40,['HTTP 写入','/write/:db'],'blue'),(330,['Line parser','Point / 表映射'],'blue'),(620,['DataCache','Vec<RecordBatch>'],'teal'),(910,['Flush / Writer','生成 L0 文件'],'teal')]:f.box(x,155,250,100,lines,tone)
for x in [290,580,870]:f.line([(x,205),(x+40,205)])
f.line([(1035,255),(1035,480)])
f.text(1055,350,'落盘',19,MUTED)
for x,lines,tone in [(40,['HTTP / Flight','MySQL 查询入口'],'blue'),(330,['QueryEngine','发现与注册表'],'blue'),(620,['DataFusion','SQL 规划与执行'],'blue'),(910,['Parquet 文件','日期分区目录'],'teal')]:f.box(x,480,250,110,lines,tone)
for x in [290,580,870]:f.line([(x,535),(x+40,535)])
f.box(330,320,540,75,['第一版先完成文件查询','写缓存查询在后续接入'],'gray',20)
f.text(40,655,'写入、内存批次、文件存储和 SQL 执行各自负责一个清晰的环节。',20,MUTED)
figs.append(f.finish('''flowchart TB
  W[HTTP write] --> P[Parser / Point]
  P --> C[DataCache / RecordBatch]
  C --> F[Flush / ParquetWriter]
  F --> D[(Partitioned Parquet files)]
  Q[HTTP / Flight / MySQL query] --> E[QueryEngine / discovery]
  E --> DF[DataFusion]
  DF -->|read| D
  N[First implement queries over persisted files]
'''))

f=Figure('02-data-model','02 / 一行协议如何映射到一张表','先约定表名映射，再让 tags、fields 和时间戳进入统一数据模型。',740)
f.box(40,150,1120,90,['POST /write/demo','cpu,service=web,host=server01 usage=23.5 <timestamp>'],'blue',21)
for x,head,value in [(40,'URL 中的 db','catalog = demo'),(435,'service 标签','schema = web'),(830,'measurement','table = cpu')]:
 f.box(x,310,330,100,[head,value],'teal')
for x in [205,600,995]:f.line([(x,240),(x,310)])
f.box(40,490,1120,82,['逻辑表 demo.web.cpu → data/demo/web/cpu/date=2025-12-27/'],'blue',23)
for x in [205,600,995]:f.line([(x,410),(x,490)])
f.box(40,600,1120,64,['timestamp → 时间列与日期分区；tags → 字符串列；usage → 浮点列'],'teal',20)
figs.append(f.finish('''flowchart TB
  A[POST /write/demo + line protocol] --> B[catalog: demo]
  A --> C[schema: web from service tag]
  A --> D[table: cpu from measurement]
  B --> T[demo.web.cpu]
  C --> T
  D --> T
  T --> F[data/demo/web/cpu/date=YYYY-MM-DD/]
  A --> X[Preserve timestamp, tags, and numeric fields]
'''))

f=Figure('03-record-batch','03 / 从行数据转换为 Arrow 列数组','按列收集时间戳、标签和指标值；所有列数组必须具有相同的行数。',670)
f.box(40,170,475,225,['行 1：t0 / server01 / cn / 23.5','行 2：t1 / server02 / cn / 42.0','HTTP 中连续到达的指标'],'blue',22)
f.line([(515,280),(655,280)])
f.text(543,225,'列式转换',20,MUTED)
f.box(655,150,505,300,['timestamp  [t0, t1]','measurement  [cpu, cpu]','host  [server01, server02]','region  [cn, cn]','usage  [23.5, 42.0]','Schema + 等长 Arrays = RecordBatch'],'teal',22)
f.box(40,500,1120,88,['先收集整批数据的列集合，再逐列构造数组。','缺少的值补 NULL；列顺序与 Schema 保持一致。'],'gray',21)
figs.append(f.finish('''flowchart LR
  A[Rows: timestamps / tags / numeric fields] --> B[Collect column names]
  B --> C[Build equal-length Arrow arrays]
  C --> D[Schema + arrays]
  D --> E[RecordBatch]
  N[Collect column names across the entire batch]
'''))

f=Figure('04-buffer-flush','05 / 缓存、确认与刷盘触发','200 表示写入缓存；三种触发方式最终调用同一个 flush。',850)
f.box(40,160,245,100,['Point 批次','转为 RecordBatch'],'blue')
f.box(365,160,245,100,['检查估算容量','是否还有空间？'],'blue')
f.box(710,160,450,100,['加入分区对应的 Vec<RecordBatch>','更新数组内存计数'],'teal')
f.line([(285,210),(365,210)]);f.line([(610,210),(710,210)])
f.text(640,175,'是',18,MUTED)
f.line([(487,260),(487,320)]);f.box(365,320,245,85,['容量不足 → HTTP 503'],'orange',19)
f.line([(935,260),(935,320)]);f.box(710,320,450,85,['HTTP 200：Data added to cache'],'blue',21)
for x,lines in [(40,['周期定时器','flush_interval_secs']),(435,['达到缓存 80%','Notify 通知']),(830,['显式调用','POST /flush'])]:f.box(x,490,330,95,lines,'gray',21)
f.box(350,665,500,85,['DataCache::flush → ParquetWriter'],'teal',23)
f.line([(205,585),(205,707),(350,707)])
f.line([(600,585),(600,665)])
f.line([(995,585),(995,707),(850,707)])
figs.append(f.finish('''flowchart TB
  A[Points to RecordBatch] --> B{Estimated cache capacity available?}
  B -->|yes| C[Append batch and update counter]
  B -->|no| R[HTTP 503]
  C --> ACK[HTTP 200: added to cache]
  T[Timer] --> F[DataCache flush]
  N[80 percent Notify] --> F
  M[POST /flush] --> F
  F --> P[ParquetWriter]
'''))

f=Figure('05-schema-alignment','04 / 多个批次怎样写进一个 Parquet 文件','先合并列集合，再按列名对齐；缺列补 NULL，类型冲突按规则处理。',780)
f.box(40,160,500,120,['Batch A','timestamp / measurement / host'],'blue',23)
f.box(660,160,500,120,['Batch B','timestamp / measurement / host / region'],'blue',21)
f.box(300,355,600,110,['按列名合并 Schema','同名列类型冲突 → 返回错误'],'teal',23)
f.line([(290,280),(290,410),(300,410)])
f.line([(910,280),(910,410),(900,410)])
f.box(40,540,500,110,['对齐 A：region = NULL','已有列按目标字段顺序重排'],'gray',22)
f.box(660,540,500,110,['对齐 B：保留 region','已有列按目标字段顺序重排'],'gray',22)
f.line([(450,465),(450,500),(290,500),(290,540)])
f.line([(750,465),(750,500),(910,500),(910,540)])
f.text(40,690,'随后由 ArrowWriter 顺序写入各批次，并 close 完成文件写出。',21,MUTED)
figs.append(f.finish('''flowchart TB
  A[Batch A: timestamp / measurement / host] --> M[Merge schemas by column name]
  B[Batch B: timestamp / measurement / host / region] --> M
  M --> C[Align A: region is NULL]
  M --> D[Align B: preserve region]
  M -->|type conflict| E[Error]
  C --> W[ArrowWriter write and close]
  D --> W
'''))

f=Figure('06-query-path','06 / SQL 查询的调用顺序','表发现与注册由数据库完成；SQL 规划执行交给 DataFusion。',900)
centers=[165,455,745,1035]
for x,label in zip(centers,['HTTP 查询','QueryEngine','DataFusion','文件系统']):
 f.box(x-125,150,250,70,[label],'blue',22)
 f.line([(x,230),(x,805)],False,True)
for y,a,b,label in [(285,165,455,'1. SQL + 数据库上下文'),(355,455,1035,'2. 发现 schema / table / date 目录'),(425,455,745,'3. 注册 Parquet ListingTable'),(495,455,745,'4. ctx.sql(sql)'),(565,745,1035,'5. 扫描已落盘 Parquet'),(635,1035,745,'6. 文件数据'),(705,745,455,'7. collect() → RecordBatch'),(775,455,165,'8. 转为 JSON 返回')]:
 f.line([(a,y),(b,y)])
 f.text(min(a,b)+10,y-36,label,19,MUTED)
figs.append(f.finish('''sequenceDiagram
  participant H as HTTP
  participant Q as QueryEngine
  participant D as DataFusion
  participant F as Filesystem
  H->>Q: SQL and database context
  Q->>F: Discover catalogs, tables, date partitions
  Q->>D: Register Parquet ListingTable
  Q->>D: ctx.sql(sql)
  D->>F: Scan persisted Parquet
  F-->>D: File data
  D-->>Q: collect RecordBatches
  Q-->>H: JSON result
'''))

f=Figure('07-compaction','07 / Compaction：合并小文件，管理有效文件集合','读出批次、写入大文件，再切换可见文件集合并回收旧文件。',760)
f.box(40,160,300,160,['L0_a.parquet','L0_b.parquet','L0_c.parquet'],'blue',24)
f.box(450,185,300,110,['读取批次','对齐 schema'],'blue',24)
f.box(860,185,300,110,['写入下一层文件','L1_new.parquet'],'teal',23)
f.line([(340,240),(450,240)]);f.line([(750,240),(860,240)])
f.text(40,385,'文件生命周期',23,INK)
for x,lines,tone in [(40,['写入新文件','保留输入文件'],'teal'),(450,['切换有效文件集合','查询只读有效文件'],'blue'),(860,['回收旧文件','完成本次合并'],'gray')]:f.box(x,450,300,120,lines,tone,21)
f.line([(340,510),(450,510)]);f.line([(750,510),(860,510)])
f.box(40,625,1120,65,['核心约束：每条记录只读一次；有效文件切换与旧文件回收需要协调。'],'gray',20)
figs.append(f.finish('''flowchart TB
  A[L0 files] --> B[Read batches and align schemas]
  B --> C[Write next-level file]
  C --> W[Switch active file set]
  W --> D[Reclaim old input files]
  W --> Q[Queries read active files only]
'''))

f=Figure('08-ack-durability','08 / 写入确认、查询可见性与恢复是三个问题','先约定响应含义；基础版确认数据进入内存，后续用 WAL 补充恢复路径。',740)
for x,lines,tone in [(40,['进入内存缓存','暂存 RecordBatch'],'blue'),(335,['返回 HTTP 200','确认接收'],'blue'),(630,['显式 / 后台 flush','生成 Parquet'],'teal'),(925,['表发现后查询','读取文件中的记录'],'teal')]:f.box(x,165,235,120,lines,tone,21)
for x in [275,570,865]:f.line([(x,225),(x+60,225)])
f.box(40,395,530,170,['flush 前退出 / 写入失败','未落盘数据可能丢失','WAL 为未刷盘数据提供恢复路径'],'orange',23)
f.box(630,395,530,170,['显式 flush 后重新启动','检查文件与查询结果','单独验证持久化数据的读取'],'gray',23)
f.text(40,625,'下一步：在确认写入之前追加 WAL，并在启动时重放未完成的记录。',23,MUTED)
figs.append(f.finish('''flowchart LR
  C[In-memory cache] --> A[HTTP 200]
  A --> F[Explicit or background flush]
  F --> P[Parquet files]
  P --> Q[Discover table and query]
  C -.-> R[Exit before flush: loss risk without WAL]
  P -.-> N[Normal restart check is not power-loss recovery validation]
'''))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')
body=markdown.markdown((ROOT/'article.md').read_text(),extensions=['tables','fenced_code','toc'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MynaDB 从零实现系列 01</title><style>
:root{color-scheme:light}body{margin:0;background:#f3f6fa;color:#233749;font:17px/1.95 system-ui,-apple-system,"Microsoft YaHei",sans-serif}main{max-width:1000px;margin:36px auto;padding:48px 54px;background:white;border:1px solid #e1e8ef;border-radius:16px}h1{font-size:34px;line-height:1.5;letter-spacing:-.6px}h2{font-size:25px;margin-top:48px;padding-top:12px;border-top:1px solid #e2e9ef}a{color:#096d8f}p{margin:20px 0}img{display:block;width:100%;height:auto;margin:28px 0;border:1px solid #e3eaf0;border-radius:10px}pre{padding:22px;background:#112b3c;color:#e2edf5;overflow:auto;border-radius:10px;font:14px/1.8 ui-monospace,monospace}code{font-family:ui-monospace,monospace;font-size:.9em}p code,td code,li code{background:#eef3f8;padding:2px 5px;border-radius:4px}table{border-collapse:collapse;width:100%;font-size:15px;margin:24px 0}td,th{border:1px solid #dce5ed;padding:12px;text-align:left}th{background:#edf5f9}li{margin:8px 0}strong{color:#123c52}.draft{font-size:14px;color:#617a8d;border-bottom:1px solid #e0e8ef;padding-bottom:15px}@media(max-width:700px){main{margin:0;padding:24px 18px;border:0;border-radius:0}h1{font-size:27px}table{display:block;overflow:auto}pre{padding:15px}}
</style><main><p class="draft">社区文章草稿 · 单机基础设计 · 本地预览，尚未对外发表</p>'''+body+'</main></html>'
(ROOT/'preview.html').write_text(page)
print('Generated',len(figs),'PNG/SVG/Mermaid figures and preview.html')
