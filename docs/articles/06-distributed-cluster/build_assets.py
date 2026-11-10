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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 06 · 分布式集群',15,MUTED)
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
f=Figure('01-cluster-roles','06 / 从单机拆分到多个角色','Router 负责入口和协调，Data 执行，Meta 管理元数据。',740)
f.box(40,170,330,135,['客户端', '写入 / SQL'],'blue',20)
f.box(435,170,330,135,['Router', '路由 / 查询协调'],'teal',20)
f.box(830,170,330,135,['Data 与 Meta', '数据执行 / 元数据'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['共享存储保存数据，不代替节点协调协议。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[客户端] --> B[Router]\n  B --> C[Data 与 Meta]\n  N[共享存储保存数据，不代替节点协调协议。]'))
f=Figure('02-write-routing','06 / 写入如何到达 Data 节点','Router 解析并按分区组织 Arrow RecordBatch。',740)
f.box(40,170,330,135,['客户端请求', 'Line protocol'],'blue',20)
f.box(435,170,330,135,['Router', '解析 / 分区 / 选路'],'teal',20)
f.box(830,170,330,135,['Data 节点', 'Flight 接收并处理'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['部分成功与超时重试需要明确结果和幂等语义。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[客户端请求] --> B[Router]\n  B --> C[Data 节点]\n  N[部分成功与超时重试需要明确结果和幂等语义。]'))
f=Figure('03-query-fanout','06 / 分布式查询与结果汇总','根据路由信息选择节点，汇总结果时保留 SQL 语义。',740)
f.box(40,170,330,135,['SQL 查询', '选择目标节点'],'blue',20)
f.box(435,170,330,135,['Data 节点', '并行读取与计算'],'teal',20)
f.box(830,170,330,135,['Router', '汇总 / 返回结果'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['AVG、排序与 LIMIT 等需要正确的全局处理。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[SQL 查询] --> B[Data 节点]\n  B --> C[Router]\n  N[AVG、排序与 LIMIT 等需要正确的全局处理。]'))
f=Figure('04-meta-raft','06 / Meta 使用 Raft 协调控制面','Raft 复制元数据状态变更，不自动复制所有指标数据。',740)
f.box(40,170,330,135,['元数据请求', '发送至 leader'],'blue',20)
f.box(435,170,330,135,['Raft 多数派', '复制并提交日志'],'teal',20)
f.box(830,170,330,135,['状态机', '应用元数据变更'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['外部数据写入和路由一致性仍需独立协议与验证。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[元数据请求] --> B[Raft 多数派]\n  B --> C[状态机]\n  N[外部数据写入和路由一致性仍需独立协议与验证。]'))
f=Figure('05-routing-cache','06 / 元数据变化后如何刷新路由','缓存提高效率，过期时必须阻止失效的写入者。',740)
f.box(40,170,330,135,['Meta 变更', '节点 / 分区信息'],'blue',20)
f.box(435,170,330,135,['Router 刷新', '更新路由缓存'],'teal',20)
f.box(830,170,330,135,['Data 校验', '拒绝无权写入'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['授权、fencing 和重试需要端到端验证。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[Meta 变更] --> B[Router 刷新]\n  B --> C[Data 校验]\n  N[授权、fencing 和重试需要端到端验证。]'))
f=Figure('06-failure-scenarios','06 / 不同故障影响不同层次','故障矩阵应同时检查可用性、已确认写入和完整结果。',740)
f.box(40,170,330,135,['Router / Data 故障', '入口与未持久化数据'],'blue',20)
f.box(435,170,330,135,['Meta / 网络分区', '多数派与写入授权'],'teal',20)
f.box(830,170,330,135,['对象存储故障', 'flush / 查询 / 恢复'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['这些是建议验证的场景，不是已完成测试。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[Router / Data 故障] --> B[Meta / 网络分区]\n  B --> C[对象存储故障]\n  N[这些是建议验证的场景，不是已完成测试。]'))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
