/* Andrade Construction LLC — script.js
   Mobile nav · Gallery filter · Lightbox · Before/After slider */

(function () {
  'use strict';

  /* Language: English lives at /, Spanish at /es/. The EN/ES toggle in the
     header is a pair of plain links written by tools/build_site.py. */

  /* ── Mobile nav ────────────────────────────────────────────── */
  const navToggle = document.querySelector('.nav-toggle');
  if (navToggle) {
    navToggle.addEventListener('click', () => {
      document.body.classList.toggle('nav-open');
      const open = document.body.classList.contains('nav-open');
      navToggle.setAttribute('aria-expanded', open);
    });

    // close on nav link click
    document.querySelectorAll('.site-nav a').forEach(a => {
      a.addEventListener('click', () => {
        document.body.classList.remove('nav-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ── Gallery filter ────────────────────────────────────────── */
  const filterBtns = document.querySelectorAll('.gallery-filter button');
  if (filterBtns.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.dataset.filter;
        filterBtns.forEach(b => b.setAttribute('aria-pressed', 'false'));
        btn.setAttribute('aria-pressed', 'true');

        // Filter individual items (legacy masonry)
        document.querySelectorAll('.gallery__item[data-cat]').forEach(item => {
          if (cat === 'all' || item.dataset.cat === cat) item.classList.remove('is-hidden');
          else item.classList.add('is-hidden');
        });
        // Filter whole job blocks (new job-based portfolio)
        document.querySelectorAll('.job-block[data-cat]').forEach(jb => {
          if (cat === 'all' || jb.dataset.cat === cat) jb.classList.remove('is-hidden');
          else jb.classList.add('is-hidden');
        });
      });
    });
  }

  /* ── Lightbox ──────────────────────────────────────────────── */
  const lb          = document.querySelector('.lightbox');
  const lbImg       = lb && lb.querySelector('img');
  const lbClose     = lb && lb.querySelector('.lightbox__close');
  const lbPrev      = lb && lb.querySelector('.lightbox__prev');
  const lbNext      = lb && lb.querySelector('.lightbox__next');
  let galleryItems  = [];
  let lbIndex       = 0;

  function openLightbox(items, idx) {
    galleryItems = items;
    lbIndex      = idx;
    showLbImage(lbIndex);
    lb.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lb.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  function showLbImage(i) {
    lbImg.src = galleryItems[i].dataset.src || galleryItems[i].querySelector('img').src;
    lbImg.alt = galleryItems[i].dataset.label || '';
  }

  if (lb) {
    lbClose.addEventListener('click', closeLightbox);
    lb.addEventListener('click', e => { if (e.target === lb) closeLightbox(); });

    if (lbPrev) lbPrev.addEventListener('click', () => {
      lbIndex = (lbIndex - 1 + galleryItems.length) % galleryItems.length;
      showLbImage(lbIndex);
    });
    if (lbNext) lbNext.addEventListener('click', () => {
      lbIndex = (lbIndex + 1) % galleryItems.length;
      showLbImage(lbIndex);
    });

    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape')     closeLightbox();
      if (e.key === 'ArrowLeft')  { lbIndex = (lbIndex - 1 + galleryItems.length) % galleryItems.length; showLbImage(lbIndex); }
      if (e.key === 'ArrowRight') { lbIndex = (lbIndex + 1) % galleryItems.length; showLbImage(lbIndex); }
    });

    document.querySelectorAll('.gallery__item').forEach((item, _, all) => {
      item.addEventListener('click', e => {
        e.preventDefault();
        const visible = Array.from(all).filter(x => !x.classList.contains('is-hidden'));
        openLightbox(visible, visible.indexOf(item));
      });
    });
  }

  /* ── Before/After slider (clip-path + pointer events) ──────── */
  document.querySelectorAll('.beforeafter').forEach(el => {
    let activePointer = null;

    function setPosFromX(x) {
      const rect = el.getBoundingClientRect();
      let pct = ((x - rect.left) / rect.width) * 100;
      pct = Math.max(2, Math.min(98, pct));
      el.style.setProperty('--pos', pct + '%');
    }

    el.addEventListener('pointerdown', e => {
      activePointer = e.pointerId;
      try { el.setPointerCapture(e.pointerId); } catch (_) {}
      setPosFromX(e.clientX);
      e.preventDefault();
    });
    el.addEventListener('pointermove', e => {
      if (activePointer === e.pointerId) {
        setPosFromX(e.clientX);
        e.preventDefault();
      }
    });
    function endPointer(e) {
      if (activePointer === e.pointerId) {
        try { el.releasePointerCapture(e.pointerId); } catch (_) {}
        activePointer = null;
      }
    }
    el.addEventListener('pointerup',     endPointer);
    el.addEventListener('pointercancel', endPointer);
    el.addEventListener('pointerleave',  endPointer);

    // Keyboard accessibility
    el.tabIndex = 0;
    el.addEventListener('keydown', e => {
      const cur = parseFloat(el.style.getPropertyValue('--pos')) || 50;
      if (e.key === 'ArrowLeft')  { el.style.setProperty('--pos', Math.max(2, cur - 4) + '%'); e.preventDefault(); }
      if (e.key === 'ArrowRight') { el.style.setProperty('--pos', Math.min(98, cur + 4) + '%'); e.preventDefault(); }
    });
  });

  /* ── Active nav link ───────────────────────────────────────── */
  const here = window.location.pathname.replace(/index\.html$/, '');
  document.querySelectorAll('.site-nav a').forEach(a => {
    const path = new URL(a.href, window.location.href).pathname.replace(/index\.html$/, '');
    // exact match, or a detail page under the section (services.html -> /services/…)
    const section = path.replace(/\.html$/, '/');
    if (here === path || (section.length > 1 && here.startsWith(section))) {
      a.setAttribute('aria-current', 'page');
    }
  });

  /* ── Form spam protection (honeypot hide) ──────────────────── */
  document.querySelectorAll('.hp-field').forEach(el => { el.style.display = 'none'; });

})();
