"""Generate the engineering index and article readers from existing Markdown.

Run from any directory with Python's Markdown package installed. Existing image
and preview URLs are retained; article.md remains the source of each chapter.
"""
from pathlib import Path
from html import escape
from urllib.parse import urljoin
import json
import math
import os
import re
import markdown

ARTICLES = Path(__file__).resolve().parent
SITE = ARTICLES.parent.parent
PUBLIC = 'https://panbooks.github.io/mynadb-portal/'
SERIES = '从0到1实现一个分布式时序数据库'
STAGES = [
    ('foundations', '01', '单机基础', '先把数据写进去、存下来，再让查询及时看见它。', range(1, 6)),
    ('cluster', '02', '分布式架构', '拆分节点职责，处理恢复、退役与分区路由。', range(6, 9)),
    ('operations', '03', '运维与正确性', '连接使用者与采集生态，让结果和能力边界可验证。', range(9, 11)),
]


def chapters():
    items = []
    for folder in sorted(ARTICLES.glob('[0-9][0-9]-*')):
        if not (folder / 'article.md').is_file():
            continue
        source = (folder / 'article.md').read_text()
        title = source.splitlines()[0].removeprefix('# ')
        summary = (folder / 'summary.md').read_text().strip()
        images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', source)
        prose = re.sub(r'```.*?```', '', source, flags=re.S)
        units = len(re.findall(r'[\u4e00-\u9fff]', prose)) + len(re.findall(r'\b[A-Za-z]+\b', prose))
        number = int(folder.name[:2])
        stage = next(s for s in STAGES if number in s[4])
        items.append(dict(folder=folder, number=number, title=title, short=title.split('：', 1)[-1],
                          summary=summary, source=source, images=images, stage=stage,
                          minutes=max(3, math.ceil(units / 400 + len(images) / 4))))
    return items


def relative(page, target):
    return os.path.relpath(SITE / target, page.parent).replace(os.sep, '/')


def nav(page):
    def href(target): return escape(relative(page, target), quote=True)
    return f'''<a class="skip-link" href="#main-content">跳到正文</a>
<nav class="navbar" aria-label="主导航"><div class="container">
<a href="{href('zh/index.html')}" class="navbar-brand"><img src="{href('images/logo-icon.svg')}" alt="" class="logo-img" width="40" height="40">MynaDB</a>
<ul class="navbar-nav" id="primary-navigation">
<li><a href="{href('zh/docs/index.html')}">文档</a></li>
<li><a href="{href('zh/docs/quickstart.html')}">快速开始</a></li>
<li><a href="{href('zh/docs/architecture.html')}">架构</a></li>
<li><a href="{href('docs/articles/index.html')}" class="active" aria-current="page">技术专栏</a></li>
<li><a href="{href('zh/docs/api.html')}">API 参考</a></li>
<li><a href="{href('zh/docs/examples.html')}">示例</a></li>
</ul>
<div class="navbar-actions"><a class="engineering-language" href="{href('index.html')}" lang="en">English site</a><a class="btn btn-secondary engineering-github" href="https://github.com/panbooks/mynadb" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>
<button class="mobile-menu-btn" type="button" aria-label="打开导航" aria-controls="primary-navigation" aria-expanded="false">☰</button>
</div></nav>'''


def footer(page):
    return f'''<footer class="engineering-footer"><div><a href="{escape(relative(page, 'docs/articles/index.html'))}">MynaDB 技术专栏</a><span>用清晰的设计理解数据系统。</span></div><a href="https://github.com/panbooks/mynadb-portal" target="_blank" rel="noopener noreferrer">在 GitHub 查看文档 ↗</a></footer>'''


def page_html(page, title, description, content, kind='website', image=None):
    canonical = urljoin(PUBLIC, str(page.relative_to(SITE)))
    image_tag = f'<meta property="og:image" content="{escape(image, quote=True)}">' if image else ''
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="{kind}">{image_tag}
<link rel="icon" type="image/svg+xml" href="{relative(page, 'images/favicon.svg')}">
<link rel="stylesheet" href="{relative(page, 'css/style.css')}"><link rel="stylesheet" href="{relative(page, 'css/articles.css')}">
<script src="{relative(page, 'js/articles.js')}" defer></script></head>
<body class="engineering-site">{nav(page)}{content}{footer(page)}<p class="sr-only" id="reader-status" role="status" aria-live="polite"></p></body></html>'''


def series_list(page, items, current):
    lines = []
    for item in items:
        active = item['number'] == current
        target = relative(page, str((item['folder'] / 'preview.html').relative_to(SITE)))
        lines.append(f'''<li><a href="{escape(target)}"{' class="is-current" aria-current="page"' if active else ''}><span class="chapter-number">{item['number']:02}</span><span>{escape(item['short'])}</span></a></li>''')
    return '<ol class="series-chapters">' + ''.join(lines) + '</ol>'


def render_article(root):
    root = Path(root).resolve()
    items = chapters()
    item = next(item for item in items if item['folder'] == root)
    page = root / 'preview.html'
    index_link = relative(page, 'docs/articles/index.html')
    reader = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    source = item['source'].split('\n', 1)[1]
    # Existing cross-chapter Markdown links now open the complete reader.
    source = re.sub(r'(\]\([^\s)]*)article\.md(?=[#)])', r'\1preview.html', source)
    body = reader.convert(source)
    body = body.replace('<img ', '<img loading="lazy" decoding="async" ')
    directory = series_list(page, items, item['number'])
    toc = reader.toc
    prefix, short = item['title'].split('：', 1)
    previous = next((a for a in items if a['number'] == item['number'] - 1), None)
    following = next((a for a in items if a['number'] == item['number'] + 1), None)
    def pager_link(other, label):
        if not other:
            return f'<a class="chapter-pager-link" href="{index_link}"><span>{label}</span><strong>返回系列目录</strong></a>'
        target = relative(page, str((other['folder'] / 'preview.html').relative_to(SITE)))
        return f'<a class="chapter-pager-link" href="{target}"><span>{label} · 第 {other["number"]:02} 篇</span><strong>{escape(other["short"])}</strong></a>'
    content = f'''<div class="reader-layout">
<aside class="series-sidebar" aria-label="系列目录"><a class="sidebar-home" href="{index_link}">← 技术专栏</a><p class="sidebar-eyebrow">从单机到分布式</p><h2>{SERIES}</h2><p class="sidebar-progress">第 {item['number']:02} 篇 / 共 {len(items)} 篇</p>{directory}</aside>
<main class="article-main" id="main-content"><header class="article-header">
<div class="article-breadcrumb"><a href="{index_link}">技术专栏</a><span aria-hidden="true">/</span><span>{escape(item['stage'][2])}</span></div>
<p class="article-meta">第 {item['number']:02} 篇 <span>·</span> 约 {item['minutes']} 分钟 <span>·</span> {len(item['images'])} 张图解</p>
<h1><span class="article-series-name">{escape(prefix)}：</span>{escape(short)}</h1><p class="article-summary">{escape(item['summary'])}</p>
<details class="mobile-chapter-menu"><summary>系列目录 · 当前第 {item['number']:02} 篇</summary>{directory}</details>
<details class="mobile-page-toc"><summary>本篇目录</summary>{toc}</details></header>
<article class="article-body">{body}</article>
<nav class="chapter-pager" aria-label="篇章导航">{pager_link(previous, '← 上一篇')}{pager_link(following, '下一篇 →')}</nav>
<section class="article-resources" aria-labelledby="resources-title"><h2 id="resources-title">保存与分享</h2><p>下载带公网图片链接的 Markdown，或复制摘要，方便保存和社区分享。</p><div class="article-resource-actions"><button class="btn btn-primary" type="button" data-copy-file="article.publish.md">复制发布版 Markdown</button><button class="btn btn-secondary" type="button" data-copy-file="summary.md">复制摘要</button><a class="text-link" href="article.publish.md" download>下载 Markdown ↓</a></div></section>
</main><aside class="page-toc" aria-label="本篇目录"><h2>本篇目录</h2>{toc}<a class="toc-back" href="#main-content">回到顶部 ↑</a></aside></div>
<dialog class="image-dialog" aria-label="架构图大图"><div class="image-dialog-toolbar"><span>架构图</span><a class="image-original" target="_blank" rel="noopener noreferrer">打开原图 ↗</a><button type="button" class="image-dialog-close" aria-label="关闭大图">关闭 ×</button></div><img alt=""><p class="image-dialog-caption"></p></dialog>'''
    image = urljoin(PUBLIC, str((root / item['images'][0]).relative_to(SITE))) if item['images'] else None
    page.write_text(page_html(page, item['title'] + ' · MynaDB 技术专栏', item['summary'], content, 'article', image))


def render_index():
    items = chapters()
    page = ARTICLES / 'index.html'
    total_images = sum(len(item['images']) for item in items)
    first = items[0]['folder'].name + '/preview.html'
    groups = []
    for key, number, title, description, numbers in STAGES:
        cards = []
        for item in items:
            if item['number'] not in numbers:
                continue
            target = item['folder'].name + '/preview.html'
            cards.append(f'''<a class="chapter-card" href="{target}"><div class="chapter-card-top"><span class="chapter-card-number">{item['number']:02}</span><span>约 {item['minutes']} 分钟 · {len(item['images'])} 张图</span></div><h3>{escape(item['short'])}</h3><p>{escape(item['summary'])}</p><span class="chapter-card-link">阅读第 {item['number']:02} 篇 <span aria-hidden="true">↗</span></span></a>''')
        groups.append(f'''<section class="course-stage" id="{key}" aria-labelledby="stage-{key}"><header class="course-stage-header"><span class="stage-number">{number}</span><div><h2 id="stage-{key}">{title}</h2><p>{description}</p></div></header><div class="chapter-grid">{''.join(cards)}</div></section>''')
    content = f'''<main id="main-content"><section class="course-hero"><div class="course-hero-grid"><div><p class="engineering-eyebrow">技术专栏 / 架构实践</p><h1>从0到1实现一个<br><span>分布式时序数据库</span></h1><p class="course-lead">从一条指标的写入开始，理解存储、查询与恢复，<br class="desktop-break">再走向多节点协调、路由和运维。</p><div class="course-facts"><span>{len(items)} 篇系列文章</span><span>{total_images} 张架构图</span><span>Rust / Arrow / Parquet</span></div><div class="course-actions"><a class="btn btn-primary" href="{first}">从第一篇开始 <span aria-hidden="true">→</span></a><a class="btn btn-secondary" href="#chapters">查看全部篇目 ↓</a></div></div><aside class="learning-path" aria-label="学习路线"><p class="path-eyebrow">一条完整的实现路线</p><ol><li><span>01</span><div><strong>打通单机读写</strong><small>HTTP → Arrow → Parquet → SQL</small></div></li><li><span>02</span><div><strong>建立存储与恢复边界</strong><small>WAL · 复制 · 对象存储</small></div></li><li><span>03</span><div><strong>走向分布式架构</strong><small>Router · Data · Meta · Raft</small></div></li><li><span>04</span><div><strong>连接运维与数据生态</strong><small>可观测性 · 协议接入 · 正确性</small></div></li></ol></aside></div></section>
<div class="course-layout" id="chapters"><aside class="course-overview"><p class="engineering-eyebrow">阅读指南</p><h2>按顺序理解，<br>也可以按需阅读。</h2><p>适合有编程基础、希望了解数据库内部实现的开发者。前五篇铺垫单机能力，第六篇开始进入分布式设计。</p><nav aria-label="学习阶段"><a href="#foundations">01 · 单机基础</a><a href="#cluster">02 · 分布式架构</a><a href="#operations">03 · 运维与正确性</a></nav><p class="course-note">文章结合 MynaDB 的开发里程碑讲设计。代码示意与实际实现、验证范围在正文中分别说明。</p></aside><div class="course-chapters">{''.join(groups)}</div></div>
<section class="course-end"><p>读懂架构，也动手验证。</p><a class="text-link" href="{relative(page, 'zh/docs/quickstart.html')}">前往快速开始 →</a><a class="text-link" href="https://github.com/panbooks/mynadb">查看项目源码 ↗</a></section></main>'''
    page.write_text(page_html(page, '技术专栏 · ' + SERIES + ' · MynaDB',
        '十篇图文教程，从 Rust 单机读写、WAL 与对象存储，逐步走向 Router、Data、Meta、Raft 和分布式时序数据库的运维与正确性。', content))
    data = [{'number': item['number'], 'title': item['title'], 'summary': item['summary'],
             'minutes': item['minutes'], 'images': len(item['images']),
             'stage': item['stage'][2], 'url': item['folder'].name + '/preview.html'} for item in items]
    (ARTICLES / 'catalog.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def build_site():
    for item in chapters():
        render_article(item['folder'])
    render_index()
    print('Generated engineering index, catalog and ten article readers.')


if __name__ == '__main__':
    build_site()
