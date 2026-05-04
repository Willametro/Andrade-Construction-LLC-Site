/* Andrade Construction LLC — script.js
   Mobile nav · Gallery filter · Lightbox · Before/After slider · EN/ES toggle */

(function () {
  'use strict';

  /* ── Bilingual data ─────────────────────────────────────────── */
  const i18n = {
    en: {
      'nav.services':   'Services',
      'nav.portfolio':  'Portfolio',
      'nav.about':      'About',
      'nav.contact':    'Contact',
      'nav.estimate':   'Free Estimate',
      'hero.h1':        'Built Right.\nBuilt to Last.',
      'hero.lede':      'Family-owned craftsmanship in the Salem area since 2008. Remodels, additions, and restoration — done the way they should be.',
      'hero.cta1':      'Get a Free Estimate',
      'hero.cta2':      'Call or Text (503) 999-9277',
      'hero.trust1':    'CCB #182464',
      'hero.trust2':    'Licensed, Bonded & Insured',
      'hero.trust3':    'Free Estimates',
      'services.eyebrow': 'What We Do',
      'services.h2':    'Expert Craftsmanship,\nEvery Project',
      'svc.bath.h':     'Bathroom Remodels',
      'svc.bath.p':     'Full gut-and-rebuild or targeted upgrades — tile, fixtures, layouts, and everything in between.',
      'svc.kitchen.h':  'Kitchen Remodels',
      'svc.kitchen.p':  'From cabinet refresh to full kitchen transformations that change how your home works and feels.',
      'svc.water.h':    'Water Damage Restoration',
      'svc.water.p':    'Fast, thorough remediation and rebuild after water damage, mold, or moisture intrusion.',
      'svc.addition.h': 'Home Additions',
      'svc.addition.p': 'Expand your living space with additions that match your home\'s style and construction.',
      'svc.deck.h':     'Decks & Outdoor',
      'svc.deck.p':     'Custom decks and outdoor living spaces built to Oregon weather standards and your vision.',
      'svc.floor.h':    'Flooring',
      'svc.floor.p':    'Hardwood, luxury vinyl, tile, and carpet installation done with care for lasting results.',
      'svc.remodel.h':  'Full Home Remodels',
      'svc.remodel.p':  'Whole-home transformations managed start to finish by one trusted crew.',
      'portfolio.eyebrow': 'Our Work',
      'portfolio.h2':   'Recent Projects',
      'portfolio.all':  'All Work',
      'portfolio.bath': 'Bathrooms',
      'portfolio.kit':  'Kitchens',
      'portfolio.water':'Water Damage',
      'portfolio.more': 'View Full Portfolio',
      'beforeafter.eyebrow': 'Transformations',
      'beforeafter.h2': 'See the Difference',
      'beforeafter.drag': 'Drag to compare',
      'trust.eyebrow':  'Why Andrade',
      'trust.h2':       'A Name You Can Trust',
      'trust.t1.h':     'Since 2008',
      'trust.t1.p':     'Over 15 years of building and remodeling homes across the Salem area.',
      'trust.t2.h':     'CCB Licensed',
      'trust.t2.p':     'Oregon CCB #182464 — licensed, bonded, and insured for your protection.',
      'trust.t3.h':     'Family-Owned',
      'trust.t3.p':     'Rudy and Pam Andrade run every job personally. Your home gets their full attention.',
      'trust.t4.h':     'Free Estimates',
      'trust.t4.p':     'No-pressure, no-obligation estimates. We walk the job with you before anything is signed.',
      'testi.eyebrow':  'Testimonials',
      'testi.h2':       'What Our Clients Say',
      'area.eyebrow':   'Service Area',
      'area.h2':        'Serving the Salem Region',
      'area.note':      'We primarily serve Marion, Polk, Yamhill, Linn, and Benton counties. We take projects outside this radius — call to discuss your location.',
      'cta.h2':         'Ready to Start Your Project?',
      'cta.p':          'Contact us today for a free, no-pressure estimate.',
      'cta.btn1':       'Get Free Estimate',
      'cta.btn2':       'Call or Text (503) 999-9277',
      'footer.tagline': 'Family-owned remodeling & construction in the Salem, OR area since 2008.',
      'footer.lic':     'Oregon CCB #182464 · Licensed · Bonded · Insured',
    },
    es: {
      'nav.services':   'Servicios',
      'nav.portfolio':  'Portafolio',
      'nav.about':      'Nosotros',
      'nav.contact':    'Contacto',
      'nav.estimate':   'Estimado Gratis',
      'hero.h1':        'Construido Bien.\nPara Durar.',
      'hero.lede':      'Artesanía familiar en el área de Salem desde 2008. Remodelaciones, ampliaciones y restauraciones — hechas como deben hacerse.',
      'hero.cta1':      'Obtener Estimado Gratis',
      'hero.cta2':      'Llame o Escriba (503) 999-9277',
      'hero.trust1':    'CCB #182464',
      'hero.trust2':    'Con Licencia, Fianza y Seguro',
      'hero.trust3':    'Estimados Gratis',
      'services.eyebrow': 'Lo Que Hacemos',
      'services.h2':    'Artesanía Experta,\nCada Proyecto',
      'svc.bath.h':     'Remodelación de Baños',
      'svc.bath.p':     'Renovación completa o mejoras específicas — azulejos, accesorios, distribución y mucho más.',
      'svc.kitchen.h':  'Remodelación de Cocinas',
      'svc.kitchen.p':  'Desde renovación de gabinetes hasta transformaciones completas que cambian cómo funciona su hogar.',
      'svc.water.h':    'Restauración por Daño de Agua',
      'svc.water.p':    'Remediación completa y reconstrucción después de daños por agua, moho o humedad.',
      'svc.addition.h': 'Ampliaciones del Hogar',
      'svc.addition.p': 'Amplíe su espacio con adiciones que combinan con el estilo y construcción de su hogar.',
      'svc.deck.h':     'Terrazas y Exteriores',
      'svc.deck.p':     'Terrazas personalizadas y espacios al aire libre construidos para el clima de Oregón.',
      'svc.floor.h':    'Pisos',
      'svc.floor.p':    'Instalación de madera, vinilo de lujo, baldosas y alfombra con cuidado y durabilidad.',
      'svc.remodel.h':  'Remodelación Completa',
      'svc.remodel.p':  'Transformaciones de toda la casa gestionadas de principio a fin por un equipo de confianza.',
      'portfolio.eyebrow': 'Nuestro Trabajo',
      'portfolio.h2':   'Proyectos Recientes',
      'portfolio.all':  'Todo',
      'portfolio.bath': 'Baños',
      'portfolio.kit':  'Cocinas',
      'portfolio.water':'Daño de Agua',
      'portfolio.more': 'Ver Portafolio Completo',
      'beforeafter.eyebrow': 'Transformaciones',
      'beforeafter.h2': 'Vea la Diferencia',
      'beforeafter.drag': 'Arrastre para comparar',
      'trust.eyebrow':  'Por Qué Andrade',
      'trust.h2':       'Un Nombre en el Que Confiar',
      'trust.t1.h':     'Desde 2008',
      'trust.t1.p':     'Más de 15 años construyendo y remodelando hogares en el área de Salem.',
      'trust.t2.h':     'Licencia CCB',
      'trust.t2.p':     'Oregon CCB #182464 — con licencia, fianza y seguro para su protección.',
      'trust.t3.h':     'Empresa Familiar',
      'trust.t3.p':     'Rudy y Pam Andrade supervisan cada trabajo personalmente. Su hogar recibe toda su atención.',
      'trust.t4.h':     'Estimados Gratis',
      'trust.t4.p':     'Estimados sin presión ni compromiso. Revisamos el trabajo con usted antes de firmar nada.',
      'testi.eyebrow':  'Testimonios',
      'testi.h2':       'Lo Que Dicen Nuestros Clientes',
      'area.eyebrow':   'Área de Servicio',
      'area.h2':        'Sirviendo la Región de Salem',
      'area.note':      'Servimos principalmente los condados de Marion, Polk, Yamhill, Linn y Benton. También tomamos proyectos fuera de esta área — llámenos para consultar.',
      'cta.h2':         '¿Listo para Comenzar su Proyecto?',
      'cta.p':          'Contáctenos hoy para un estimado gratis y sin presión.',
      'cta.btn1':       'Estimado Gratis',
      'cta.btn2':       'Llame o Escriba (503) 999-9277',
      'footer.tagline': 'Construcción y remodelación familiar en el área de Salem, OR desde 2008.',
      'footer.lic':     'Oregon CCB #182464 · Con Licencia · Fianza · Seguro',
    }
  };

  /* ── Lang toggle ───────────────────────────────────────────── */
  let lang = localStorage.getItem('ac_lang') || 'en';

  function applyLang(l) {
    lang = l;
    localStorage.setItem('ac_lang', l);
    document.documentElement.lang = l;

    // swap text content on elements with data-i18n attr
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      if (i18n[l] && i18n[l][key] !== undefined) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = i18n[l][key];
        } else {
          el.innerHTML = (i18n[l][key]).replace(/\n/g, '<br>');
        }
      }
    });

    // aria-pressed on toggle buttons
    document.querySelectorAll('.lang-toggle button').forEach(btn => {
      btn.setAttribute('aria-pressed', btn.dataset.lang === l ? 'true' : 'false');
    });
  }

  document.querySelectorAll('.lang-toggle button').forEach(btn => {
    btn.addEventListener('click', () => applyLang(btn.dataset.lang));
  });

  applyLang(lang);

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

        document.querySelectorAll('.gallery__item').forEach(item => {
          if (cat === 'all' || item.dataset.cat === cat) {
            item.classList.remove('is-hidden');
          } else {
            item.classList.add('is-hidden');
          }
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
      item.addEventListener('click', () => {
        const visible = Array.from(all).filter(x => !x.classList.contains('is-hidden'));
        openLightbox(visible, visible.indexOf(item));
      });
    });
  }

  /* ── Before/After slider ───────────────────────────────────── */
  document.querySelectorAll('.beforeafter').forEach(el => {
    const after   = el.querySelector('.beforeafter__after-wrap');
    const handle  = el.querySelector('.beforeafter__handle');
    let dragging  = false;

    function setPos(x) {
      const rect = el.getBoundingClientRect();
      let pct = ((x - rect.left) / rect.width) * 100;
      pct = Math.max(5, Math.min(95, pct));
      after.style.width  = pct + '%';
      handle.style.left  = pct + '%';
    }

    handle.addEventListener('mousedown',  () => { dragging = true; });
    document.addEventListener('mousemove', e => { if (dragging) setPos(e.clientX); });
    document.addEventListener('mouseup',   () => { dragging = false; });

    handle.addEventListener('touchstart', e => { dragging = true; e.preventDefault(); }, { passive: false });
    document.addEventListener('touchmove', e => {
      if (dragging) setPos(e.touches[0].clientX);
    }, { passive: true });
    document.addEventListener('touchend', () => { dragging = false; });
  });

  /* ── Active nav link ───────────────────────────────────────── */
  const current = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.site-nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === current || (current === '' && href === 'index.html')) {
      a.setAttribute('aria-current', 'page');
    }
  });

  /* ── Form spam protection (honeypot hide) ──────────────────── */
  document.querySelectorAll('.hp-field').forEach(el => { el.style.display = 'none'; });

})();
