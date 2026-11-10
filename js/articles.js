/* Progressive enhancements for the static engineering index and readers. */
(() => {
  'use strict';
  const status = document.getElementById('reader-status');
  const announce = (message) => { if (status) status.textContent = message; };

  const menu = document.querySelector('.mobile-menu-btn');
  const navigation = document.querySelector('.navbar-nav');
  if (menu && navigation) {
    const closeMenu = () => {
      navigation.classList.remove('mobile-open');
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', '打开导航');
      menu.textContent = '☰';
    };
    menu.addEventListener('click', () => {
      const open = navigation.classList.toggle('mobile-open');
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? '关闭导航' : '打开导航');
      menu.textContent = open ? '×' : '☰';
    });
    navigation.addEventListener('click', (event) => { if (event.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeMenu(); });
    window.addEventListener('resize', () => { if (window.innerWidth > 1180) closeMenu(); });
  }

  async function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const field = document.createElement('textarea');
    const previous = document.activeElement;
    field.value = text;
    field.style.cssText = 'position:fixed;left:-10000px;top:0;';
    document.body.appendChild(field);
    field.select();
    const success = document.execCommand('copy');
    field.remove();
    if (previous instanceof HTMLElement) previous.focus();
    if (!success) throw new Error('Clipboard is unavailable');
  }

  function copyButton(button, getText, successMessage) {
    button.addEventListener('click', async () => {
      const label = button.textContent;
      button.disabled = true;
      try {
        await copy(await getText());
        button.textContent = '已复制 ✓';
        announce(successMessage);
      } catch (_) {
        button.textContent = '复制失败，请重试';
        announce('复制失败，可下载 Markdown 或手动选择文字复制。');
      } finally {
        button.disabled = false;
        window.setTimeout(() => { button.textContent = label; }, 2200);
      }
    });
  }

  document.querySelectorAll('.article-body pre').forEach((pre) => {
    const code = pre.querySelector('code');
    if (!code) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'code-copy';
    button.textContent = '复制代码';
    button.setAttribute('aria-label', '复制此代码块');
    pre.appendChild(button);
    copyButton(button, () => code.textContent, '代码已复制。');
  });

  document.querySelectorAll('[data-copy-file]').forEach((button) => {
    copyButton(button, async () => {
      const response = await fetch(button.dataset.copyFile);
      if (!response.ok) throw new Error('Cannot load publication text');
      return response.text();
    }, button.dataset.copyFile === 'summary.md' ? '摘要已复制。' : '带公网图片链接的发布版 Markdown 已复制。');
  });

  const dialog = document.querySelector('.image-dialog');
  if (dialog) {
    const enlarged = dialog.querySelector('img');
    const original = dialog.querySelector('.image-original');
    const caption = dialog.querySelector('.image-dialog-caption');
    dialog.querySelector('.image-dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => document.body.classList.remove('image-modal-open'));
    document.querySelectorAll('.article-body img').forEach((image) => {
      const wrapper = document.createElement('button');
      wrapper.type = 'button';
      wrapper.className = 'image-zoom-button';
      wrapper.setAttribute('aria-label', '放大查看：' + image.alt);
      const figure = document.createElement('figure');
      const description = document.createElement('figcaption');
      description.textContent = image.alt + ' · 点击放大';
      const parent = image.parentElement;
      if (parent.tagName === 'P' && parent.children.length === 1) parent.replaceWith(figure);
      else image.before(figure);
      wrapper.appendChild(image);
      figure.append(wrapper, description);
      wrapper.addEventListener('click', () => {
        if (typeof dialog.showModal !== 'function') {
          window.open(image.currentSrc || image.src, '_blank', 'noopener');
          return;
        }
        enlarged.src = image.currentSrc || image.src;
        enlarged.alt = image.alt;
        original.href = enlarged.src;
        caption.textContent = image.alt;
        dialog.showModal();
        document.body.classList.add('image-modal-open');
      });
    });
  }

  const headings = [...document.querySelectorAll('.article-body h2[id], .article-body h3[id]')];
  const tocLinks = [...document.querySelectorAll('.page-toc .toc a')];
  if (headings.length && tocLinks.length && 'IntersectionObserver' in window) {
    const activate = (id) => tocLinks.forEach((link) => {
      const active = decodeURIComponent(link.hash.slice(1)) === id;
      link.classList.toggle('is-active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    const visible = new Set();
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) visible.add(entry.target);
        else visible.delete(entry.target);
      });
      const current = headings.find((heading) => visible.has(heading));
      if (current) activate(current.id);
    }, { rootMargin: '-100px 0px -60% 0px' });
    headings.forEach((heading) => observer.observe(heading));
    activate(headings[0].id);
  }
})();
