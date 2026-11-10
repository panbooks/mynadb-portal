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
        self.text(40,height-39,'MynaDB · 从0到1实现一个分布式时序数据库 07 · 备用节点与安全缩容',15,MUTED)
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
f=Figure('01-failure-retirement','01 / 突然故障与计划退役','两种路径的起点不同，需要分别验证。',740)
f.box(40,170,330,135,['节点故障', '租约过期等信号'],'blue',20)
f.box(435,170,330,135,['恢复协调', '识别角色与可用副本'],'teal',20)
f.box(830,170,330,135,['计划退役', '迁移 / 排空 / 关闭'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(830,237),(765,237)])
f.box(40,470,1120,115,['检测异常不能单独证明旧节点已经失去写入能力。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[节点故障] --> B[恢复协调]\n  C[计划退役] --> B\n  N[检测异常不能单独证明旧节点已经失去写入能力。]'))
f=Figure('02-no-promotion','02 / 不提升 Standby 的恢复思路','历史恢复代码中的 flush 完成检查仍有占位逻辑。',740)
f.box(40,170,330,135,['Primary 故障', '定位备用节点'],'blue',20)
f.box(435,170,330,135,['Standby', '触发复制数据 flush'],'teal',20)
f.box(830,170,330,135,['其他 Primary', '重新分配分区'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['发送 flush 命令不等于已经确认远端持久化完成。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[Primary 故障] --> B[Standby]\n  B --> C[其他 Primary]\n  N[发送 flush 命令不等于已经确认远端持久化完成。]'))
f=Figure('03-flush-checkpoint','03 / 复制进度与 flush checkpoint','只有可靠提交的连续范围，才能作为安全清理的依据。',740)
f.box(40,170,330,135,['复制批次', '101 至 105'],'blue',20)
f.box(435,170,330,135,['已提交边界', '连续范围至 103'],'teal',20)
f.box(830,170,330,135,['备用缓存', '考虑清理至 103'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['104、105 应保留；消息乱序、丢失和失败需要验证。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[复制批次] --> B[已提交边界]\n  B --> C[备用缓存]\n  N[104、105 应保留；消息乱序、丢失和失败需要验证。]'))
f=Figure('04-scale-in','04 / 计划缩容的三个阶段','以历史执行器描述为线索，具体行为需要故障测试。',740)
f.box(40,170,330,135,['迁移分区', '检查剩余容量'],'blue',20)
f.box(435,170,330,135,['退役 Primary', '拒绝新写并排空'],'teal',20)
f.box(830,170,330,135,['处理 Standby', '保护仍在服务的节点'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['超时或事件已发送，不等于迁移和持久化已经完成。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[迁移分区] --> B[退役 Primary]\n  B --> C[处理 Standby]\n  N[超时或事件已发送，不等于迁移和持久化已经完成。]'))
f=Figure('05-failure-handling','05 / 操作中断后如何继续','阶段化状态与重试是可验证设计的检查项。',740)
f.box(40,170,330,135,['执行阶段', '记录任务身份'],'blue',20)
f.box(435,170,330,135,['出现失败', '保留必要状态'],'teal',20)
f.box(830,170,330,135,['重试或停止', '检查已有结果'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['旧节点隔离必须由实际写入路径验证，不能只修改路由。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[执行阶段] --> B[出现失败]\n  B --> C[重试或停止]\n  N[旧节点隔离必须由实际写入路径验证，不能只修改路由。]'))
f=Figure('06-recovery-tests','06 / 用故障窗口验证承诺','核对客户端确认、复制进度、持久化文件与查询结果。',740)
f.box(40,170,330,135,['Primary / Standby', '故障或 flush 中断'],'blue',20)
f.box(435,170,330,135,['checkpoint', '丢失 / 乱序 / 重复'],'teal',20)
f.box(830,170,330,135,['缩容中断', '长查询与剩余容量'],'blue',20)
f.line([(370,237),(435,237)]);f.line([(765,237),(830,237)])
f.box(40,470,1120,115,['这些是建议的测试场景，不是已运行的测试。'],'gray',21)
figs.append(f.finish('flowchart LR\n  A[Primary / Standby] --> B[checkpoint]\n  B --> C[缩容中断]\n  N[这些是建议的测试场景，不是已运行的测试。]'))

(OUT/'manifest.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2)+'\n')

export_article(ROOT)
render_article(ROOT)
render_index()
print('Generated', len(figs), 'figures, preview.html and article.publish.md')
