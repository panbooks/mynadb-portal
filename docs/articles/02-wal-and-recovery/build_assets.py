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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 02 · WAL 与单机恢复设计',15,MUTED)
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
f=Figure('01-write-path','01 / 用 WAL 接管尚未刷出的写入','同步确认路径：先记录日志，再更新内存；Parquet 仍然按批次生成。',780)
for x,lines,tone in [(40,['校验与容量检查','解析完整批次'],'blue'),(330,['追加 WAL','分配递增 LSN'],'teal'),(620,['按策略同步','等待日志持久化'],'teal'),(910,['更新 Memtable','确认写入'],'blue')]:
 f.box(x,160,250,110,lines,tone,21)
for x in [290,580,870]:f.line([(x,215),(x+40,215)])
f.line([(1035,270),(1035,460)])
f.text(1055,350,'冻结批次',18,MUTED)
f.box(910,460,250,110,['批量 flush','生成 Parquet'],'teal',21)
f.box(620,460,250,110,['提交清单','文件 + checkpoint'],'blue',21)
f.box(330,460,250,110,['回收已提交日志','保留未提交记录'],'gray',21)
f.line([(910,515),(870,515)]);f.line([(620,515),(580,515)])
f.box(40,620,1120,75,['WAL 保存近期写入以便恢复；Parquet 保存批次以便查询。'],'gray',23)
figs.append(f.finish('''flowchart TB
  V[Validate input and reserve capacity] --> W[Append WAL and assign LSN]
  W --> S[Sync according to acknowledgement policy]
  S --> M[Apply to memtable and acknowledge]
  M --> F[Freeze batch and write Parquet]
  F --> C[Commit active files and checkpoint]
  C --> G[Reclaim fully committed sealed WAL segments]
'''))

f=Figure('02-durability-levels','02 / 数据在哪一层，决定确认了什么','flush 清空用户态缓冲；sync 请求文件同步，两者承担不同职责。',800)
for x,lines,tone in [(40,['用户态缓冲','BufWriter'],'blue'),(435,['操作系统缓存','底层 File 写入'],'blue'),(830,['持久化介质','同步请求完成'],'teal')]:f.box(x,170,330,120,lines,tone,23)
f.line([(370,230),(435,230)]);f.line([(765,230),(830,230)])
f.text(380,180,'flush',17,MUTED);f.text(775,180,'sync',17,MUTED)
f.box(40,405,330,145,['异步同步','提前确认，后台再同步','可能丢失近期确认记录'],'orange',21)
f.box(435,405,330,145,['每次同步','本次 sync 成功后确认','确认边界直接'],'teal',21)
f.box(830,405,330,145,['分组提交','多个请求共用一次 sync','完成后一起确认'],'teal',21)
f.box(40,625,1120,85,['新建文件还需处理目录项持久化。','同步承诺依赖操作系统、文件系统和存储设备的正确实现。'],'gray',21)
figs.append(f.finish('''flowchart TB
  B[BufWriter user-space buffer] -->|flush| O[Operating-system cache]
  O -->|file sync| D[Persistent storage]
  A[Async mode: acknowledge before sync]
  S[Per-write sync: acknowledge after sync]
  G[Group commit: share sync, then acknowledge together]
  N[File creation also requires directory durability]
'''))

f=Figure('03-record-format','03 / 让每条日志都有边界和校验','记录完整数据与接收时确定的时间戳，使重放得到同一条指标。',740)
for x,w,lines in [(40,150,['length','记录长度']),(210,130,['version','格式版本']),(360,130,['LSN','日志序号']),(510,170,['database','数据归属']),(700,270,['payload','完整批次 / 表信息']),(990,170,['checksum','完整性校验'])]:
 f.box(x,170,w,110,lines,'blue',19)
for x,lines,tone in [(40,['记录 101：完整','长度与校验通过'],'teal'),(435,['记录 102：完整','长度与校验通过'],'teal'),(830,['记录 103：写到一半','最后活跃分段的尾部'],'orange')]:
 f.box(x,385,330,120,lines,tone,21)
f.box(40,575,1120,85,['先校验长度上限，再读取并验证记录。','可识别的不完整尾部可截断；中间损坏、缺段或序号异常应停止并报告。'],'gray',21)
figs.append(f.finish('''flowchart TB
  L[length] --> V[version] --> S[LSN] --> D[database] --> P[payload] --> C[checksum]
  A[Complete record 101] --> B[Complete record 102]
  B --> T[Incomplete tail 103 in final active segment]
  T --> R[Stop at verified boundary; truncate before appending]
  E[Interior corruption, missing segment or invalid sequence: report and stop]
'''))

f=Figure('04-flush-checkpoint','04 / 同一个边界切开日志和内存','先串行 flush：所有边界内分区提交成功，才能推进 checkpoint。',900)
f.box(40,160,330,115,['旧 WAL 封口','最后 LSN = 200'],'gray',23)
f.box(435,160,330,115,['冻结旧内存批次','尚未提交且 LSN ≤ 200'],'blue',21)
f.box(830,160,330,115,['新 WAL + 新内存','从 LSN 201 继续写入'],'teal',22)
f.line([(370,215),(435,215)]);f.line([(765,215),(830,215)])
f.line([(600,275),(600,345)])
f.box(330,345,540,100,['写入并同步所有候选 Parquet 文件','此时尚未成为有效文件'],'blue',22)
f.line([(600,445),(600,515)])
f.box(330,515,540,120,['持久化发布 MANIFEST','active_files + checkpoint_lsn = 200'],'teal',22)
f.line([(600,635),(600,705)])
f.box(330,705,540,85,['回收已封口且 max LSN ≤ 200 的日志段'],'gray',22)
f.text(40,820,'候选文件未提交就不可查询；仍包含边界后记录的 WAL 分段必须保留。',21,MUTED)
figs.append(f.finish('''flowchart TB
  O[Seal old WAL at LSN 200] --> F[Freeze matching memtable prefix]
  F --> N[Continue writes from 201 in new WAL and memtable]
  F --> P[Write and sync candidate Parquet files]
  P --> C[Durably publish MANIFEST: active files and checkpoint 200]
  C --> G[Reclaim sealed WAL segments whose max LSN is at most 200]
  N --> K[Keep records after the boundary protected]
'''))

f=Figure('05-recovery','05 / 从已提交边界之后重放','启动时先恢复内部状态，再开放写入；恢复的数据不重复追加 WAL。',900)
for x,lines,tone in [(40,['读取有效 MANIFEST','加载已提交文件'],'blue'),(435,['校验所需 WAL 分段','检查顺序与完整性'],'blue'),(830,['比较每条 LSN','与 checkpoint'],'teal')]:f.box(x,160,330,110,lines,tone,21)
f.line([(370,215),(435,215)]);f.line([(765,215),(830,215)])
f.box(40,400,480,115,['LSN ≤ checkpoint','已提交，跳过重放'],'gray',23)
f.box(680,400,480,115,['LSN > checkpoint','apply_recovered → 内存'],'teal',23)
f.line([(995,270),(995,325),(280,325),(280,400)])
f.line([(995,325),(995,400)])
f.box(330,630,540,110,['恢复下一序号与日志写入状态','保留未提交 WAL，再开放请求'],'blue',23)
f.line([(280,515),(280,685),(330,685)])
f.line([(920,515),(920,685),(870,685)])
f.box(40,790,1120,55,['重放进内存并不等于已提交：再次崩溃时，原 WAL 仍需能用于恢复。'],'orange',21)
figs.append(f.finish('''flowchart TB
  M[Load committed MANIFEST and active files] --> W[Read and validate required WAL segments]
  W --> C{LSN above checkpoint?}
  C -->|no| S[Skip committed record]
  C -->|yes| A[Apply recovered record directly to memtable]
  S --> R[Restore next LSN and log writer; open service]
  A --> R
  R --> K[Keep replayed WAL until a new flush commit]
'''))

f=Figure('06-crash-windows','06 / 崩溃发生在哪一步，就读哪份可靠状态','判断依据是最后持久化的提交清单，而不是目录里有没有新文件。',830)
for x,y,lines,tone in [
 (40,160,['① 日志同步后，响应尚未返回','完整 WAL 可重放','没有响应不代表没有写入'],'blue'),
 (630,160,['② Parquet 写完，清单未发布','候选文件不参与查询','使用旧清单 + WAL 恢复'],'orange'),
 (40,465,['③ 清单已发布，旧 WAL 还在','新 checkpoint 已生效','跳过已提交记录，避免重复'],'teal'),
 (630,465,['④ 重放到内存后，再次退出','原 WAL 尚未回收','下次启动仍可重新恢复'],'blue')]:f.box(x,y,530,215,lines,tone,22)
f.text(40,745,'故障验证要核对内容、行数和重复情况；进程终止测试不能替代断电验证。',21,MUTED)
figs.append(f.finish('''flowchart TB
  A[WAL synced, response not sent] --> AR[Replay complete WAL records]
  B[Parquet written, MANIFEST not published] --> BR[Ignore candidates; use old manifest and replay WAL]
  C[MANIFEST published, old WAL not deleted] --> CR[Skip records through committed checkpoint]
  D[Recovery applied to memory, another crash] --> DR[Replay again from retained WAL]
'''))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
