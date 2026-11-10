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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 09 · 运维、接入与分析',15,MUTED)
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
f=Figure('01-ecosystem','01 / 围绕数据库内核的使用入口','不同使用者通过不同入口工作。',740)
f.box(40,170,330,135,['采集器', '指标与标签'],'blue',20)
f.box(435,170,330,135,['MynaDB', '存储 / 查询'],'teal',20)
f.box(830,170,330,135,['管理与分析', '控制台 / 图表'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['接口存在不等于所有部署角色和客户端已经验证。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[采集器] --> B[MynaDB]\n  C[管理与分析] --> B\n  N[接口存在不等于所有部署角色和客户端已经验证。]'))
f=Figure('02-console','02 / 控制台操作如何到达节点','界面需要区分空数据、部分结果和请求失败。',740)
f.box(40,170,330,135,['管理界面', '查询 / 存储浏览'],'blue',20)
f.box(435,170,330,135,['管理后端', '权限 / 转发'],'teal',20)
f.box(830,170,330,135,['Meta / Data', '状态与结果'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['真实节点状态和错误需要准确传回用户。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[管理界面] --> B[管理后端]\n  B --> C[Meta / Data]\n  N[真实节点状态和错误需要准确传回用户。]'))
f=Figure('03-protocol-mapping','03 / 协议数据到内部模型','适配协议需要检查编码、时间单位和错误语义。',740)
f.box(40,170,330,135,['指标与标签', '采集器'],'blue',20)
f.box(435,170,330,135,['协议接收与转换', '字段 / 时间映射'],'teal',20)
f.box(830,170,330,135,['内部数据点', '写入与查询'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['模型映射只是兼容性验证的起点。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[指标与标签] --> B[协议接收与转换]\n  B --> C[内部数据点]\n  N[模型映射只是兼容性验证的起点。]'))
f=Figure('04-security','04 / 请求经过哪些安全边界','不同职责需要分别配置和验证。',740)
f.box(40,170,330,135,['TLS', '保护传输'],'blue',20)
f.box(435,170,330,135,['身份与权限', '认证 / 授权'],'teal',20)
f.box(830,170,330,135,['审计', '记录操作与结果'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['必须逐部署角色和协议验证实际覆盖范围。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[TLS] --> B[身份与权限]\n  B --> C[审计]\n  N[必须逐部署角色和协议验证实际覆盖范围。]'))
f=Figure('05-streaming','05 / 写入触发查询结果更新','重新执行 SQL 并推送结果，不等于增量计算。',740)
f.box(40,170,330,135,['客户端订阅', 'WebSocket / SSE'],'blue',20)
f.box(435,170,330,135,['写入通知', '匹配关联表'],'teal',20)
f.box(830,170,330,135,['重新执行查询', '推送结果更新'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['需要检查背压、慢客户端、断线和权限。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[客户端订阅] --> B[写入通知]\n  B --> C[重新执行查询]\n  N[需要检查背压、慢客户端、断线和权限。]'))
f=Figure('06-analytics','06 / 原始数据与降采样','自动查询改写在 v0.8.0 仍未完成。',740)
f.box(40,170,330,135,['原始数据', '细粒度时序点'],'blue',20)
f.box(435,170,330,135,['降采样作业', '生成分层表'],'teal',20)
f.box(830,170,330,135,['分析查询', '显式访问 tier 表'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['需要验证桶边界、迟到数据和结果正确性。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[原始数据] --> B[降采样作业]\n  B --> C[分析查询]\n  N[需要验证桶边界、迟到数据和结果正确性。]'))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
