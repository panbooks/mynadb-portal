"""Export community Markdown with public image URLs, without changing the prose."""
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

ARTICLES = Path(__file__).resolve().parent
PUBLIC_BASE = 'https://panbooks.github.io/mynadb-portal/docs/articles/'
LINK = re.compile(r'(!?\[[^\]]*\]\()([^\s)]+)(\))')


def export_article(root):
    root = Path(root).resolve()
    source = (root / 'article.md').read_text()
    base = PUBLIC_BASE + root.name + '/'

    def public_link(match):
        target = match.group(2)
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith(('//', '#')):
            return match.group(0)
        if parsed.path.endswith('article.md'):
            # Link readers to the rendered article rather than the raw Markdown.
            target = target.replace('article.md', 'preview.html', 1)
        return match.group(1) + urljoin(base, target) + match.group(3)

    published = LINK.sub(public_link, source)
    (root / 'article.publish.md').write_text(published)
    summary = (root / 'summary.md').read_text().strip()
    if not summary or len(summary) > 100 or '\n' in summary:
        raise ValueError(f'{root.name}: summary must be one paragraph of 1–100 characters')
    return source.splitlines()[0].removeprefix('# '), summary


def export_series():
    lines = ['# 从0到1实现一个分布式时序数据库：文章摘要', '',
             '每段均不超过 100 个字符，可直接复制到社区摘要栏。', '']
    for root in sorted(ARTICLES.glob('[0-9][0-9]-*')):
        if not (root / 'article.md').is_file():
            continue
        title, summary = export_article(root)
        lines += [f'## {title}', '', summary, '',
                  f'[粘贴发布版]({root.name}/article.publish.md) · '
                  f'[图文预览]({root.name}/preview.html)', '']
    (ARTICLES / 'summaries.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for folder in sys.argv[1:]:
            export_article(folder)
    else:
        export_series()
