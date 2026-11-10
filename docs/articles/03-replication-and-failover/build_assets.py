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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 03 · 主从复制与故障切换',15,MUTED)
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
f=Figure('01-replication-overview','01 / 从单机恢复走向跨节点复制','主节点接收写入，从节点接收记录；副本状态与写入权限需要分别管理。',760)
f.box(40,160,240,110,['客户端','写入请求'],'blue',22)
f.box(390,160,330,110,['主节点 A','WAL + 内存'],'teal',22)
f.box(830,160,330,110,['从节点 B','接收 + 本地状态'],'blue',22)
f.line([(280,215),(390,215)]);f.line([(720,215),(830,215)])
f.text(735,170,'复制记录',18,MUTED)
f.box(390,390,330,100,['Parquet','批量持久化'],'gray',22)
f.box(830,390,330,100,['从节点存储','进度取决于协议'],'gray',22)
f.line([(555,270),(555,390)]);f.line([(995,270),(995,390)])
f.box(40,580,1120,85,['复制提供另一份数据来源；确认边界和安全切换仍需协议约束。'],'orange',22)
figs.append(f.finish('''flowchart LR
  C[客户端] --> A[主节点 A: WAL 和内存]
  A -->|复制记录| B[从节点 B]
  A --> P[Parquet]
  B --> S[从节点存储]
  N[确认边界和切换安全需要单独定义]
'''))

f=Figure('02-ack-boundaries','02 / 一条写入经过哪些确认边界','接收、持久化和应用是不同事件；返回成功意味着什么由策略决定。',760)
for x,lines,tone in [(40,['主节点接收','校验请求'],'blue'),(320,['主节点同步','本地 WAL'],'teal'),(600,['从节点接收','进入处理队列'],'blue'),(880,['从节点同步','应用数据'],'teal')]:f.box(x,170,240,120,lines,tone,20)
for x in [280,560,840]:f.line([(x,230),(x+40,230)])
f.box(40,420,350,120,['异步复制','本地确认后继续复制','可能丢失未复制写入'],'orange',20)
f.box(425,420,350,120,['等待远端同步','按约定的远端边界确认','等待网络与远端 I/O'],'teal',20)
f.box(810,420,350,120,['历史接收端 ACK','记录进入处理队列后发送','不证明已持久化'],'gray',20)
f.box(40,620,1120,65,['客户端超时不等于未提交；重试需要幂等或去重约定。'],'gray',21)
figs.append(f.finish('''flowchart LR
  A[主节点接收] --> B[本地日志同步]
  B --> C[从节点接收并入队]
  C --> D[从节点持久化并应用]
  E[异步：本地确认] --- B
  F[等待远端同步：协议规定边界] --- D
  G[历史 ACK：入队后发送] --- C
'''))

f=Figure('03-catch-up','03 / 从连续进度恢复复制','有序进度用于发现缺口；缺失的历史已回收时，需要快照和增量衔接。',760)
f.box(40,160,1120,95,['主节点记录：101 → 102 → 103 → 104 → 105'],'blue',23)
f.box(40,330,500,120,['从节点连续持久化到 102','连接中断，报告进度'],'gray',22)
f.box(660,330,500,120,['补发 103–105','按顺序校验、持久化与应用'],'teal',22)
f.line([(540,390),(660,390)])
f.box(40,570,1120,100,['缺失日志已回收 → 安装有明确边界的快照 → 接续后续日志','序号应关联任期；需要处理重复、缺口与数据分叉。'],'orange',21)
figs.append(f.finish('''flowchart LR
  A[主节点 101–105] --> B[从节点连续持久化到 102]
  B --> C[重连报告进度]
  C --> D[补发 103–105]
  C -->|历史不可用| E[安装快照并接续增量]
'''))

f=Figure('04-failure-detection','04 / 心跳超时不是故障证明','没有收到心跳可能是宕机，也可能是网络分区、暂停或过载。',800)
f.box(40,160,340,120,['主节点 A','可能仍在服务'],'blue',23)
f.box(820,160,340,120,['从节点 B','心跳超时，产生怀疑'],'orange',22)
f.line([(380,220),(820,220)],True,True)
f.text(500,172,'网络分区 / 延迟',21,MUTED)
f.box(40,430,340,120,['客户端仍可写 A','旧主未必停止'],'orange',21)
f.box(820,430,340,120,['B 若自行接收写入','可能出现第二个主'],'orange',21)
f.line([(210,280),(210,430)]);f.line([(990,280),(990,430)])
f.box(390,625,420,90,['超时发现异常','切换仍需授权与隔离'],'teal',21)
f.line([(380,490),(390,670)]);f.line([(820,490),(810,670)])
figs.append(f.finish('''flowchart TB
  A[主节点 A 可能仍在服务] -. 网络分区 .-> B[从节点 B 心跳超时]
  A --> C[客户端仍可写 A]
  B --> D[自行切换可能造成双主]
  C --> E[切换需要授权和隔离]
  D --> E
'''))

f=Figure('05-safe-failover','05 / 从怀疑故障到安全开放写入','以下是设计检查清单，不代表 v0.2.0 已实现完整安全切换协议。',820)
for x,lines,tone in [(40,['故障怀疑','心跳超时'],'orange'),(330,['协调授权','确保唯一任期'],'blue'),(620,['检查进度','满足协议条件'],'blue'),(910,['隔离旧主','下游验证令牌'],'teal')]:f.box(x,160,250,115,lines,tone,20)
for x in [290,580,870]:f.line([(x,218),(x+40,218)])
f.line([(1035,275),(1035,410)])
f.box(745,410,415,105,['恢复状态并更新路由','新主按协议开放写入'],'teal',21)
f.box(40,410,500,105,['旧主回归：先降级、处理分叉','再按权威历史追赶'],'gray',21)
f.line([(745,462),(540,462)])
f.box(40,645,1120,80,['fencing 令牌必须由实际写入资源验证；单纯更改角色标志不能阻止旧主。'],'orange',20)
figs.append(f.finish('''flowchart LR
  A[故障怀疑] --> B[协调授权]
  B --> C[检查候选进度]
  C --> D[下游验证 fencing 令牌]
  D --> E[恢复状态并更新路由]
  E --> F[旧主降级并追赶]
'''))

f=Figure('06-failure-windows','06 / 用故障窗口检验复制承诺','测试需核对已确认写入、缺失、重复、顺序，以及谁有权继续写入。',820)
for x,y,lines,tone in [(40,155,['① 主节点确认后失效','远端可能还未接收','检查允许的数据损失'],'orange'),(630,155,['② 远端已收到但未同步','入队 ACK 不等于持久化','中断远端并核对恢复'],'blue'),(40,455,['③ 响应丢失后客户端重试','超时不代表未提交','核对重复与幂等'],'blue'),(630,455,['④ 网络分区或旧主回归','检查授权和 fencing','防止两个有效写入者'],'orange')]:f.box(x,y,530,210,lines,tone,21)
f.text(40,745,'这些是建议的测试场景，不是已经执行的测试结果。',21,MUTED)
figs.append(f.finish('''flowchart TB
  A[主节点确认后失效] --> A1[核对允许的数据损失]
  B[远端收到但未同步] --> B1[核对恢复后的记录]
  C[客户端超时重试] --> C1[核对重复与幂等]
  D[网络分区或旧主回归] --> D1[验证授权和 fencing]
'''))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
