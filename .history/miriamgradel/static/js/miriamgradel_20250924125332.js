// static/js/miriamgradel.js
document.addEventListener('DOMContentLoaded', function () {
  /* =================== Journalism submenu =================== */
  document.querySelectorAll('.has-submenu').forEach((wrap) => {
    const btn = wrap.querySelector('.menu-toggle');
    const submenu = wrap.querySelector('.submenu');
    if (!btn || !submenu) return;

    // init closed
    submenu.hidden = true;
    btn.setAttribute('aria-expanded', 'false');
    wrap.classList.remove('open');

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation(); // block any external handler from auto-closing
      const expanded = btn.getAttribute('aria-expanded') === 'true';

      // (optional) close other submenus
      document.querySelectorAll('.has-submenu .submenu').forEach((sm) => {
        if (sm !== submenu) {
          sm.hidden = true;
          const b = sm.closest('.has-submenu')?.querySelector('.menu-toggle');
          if (b) b.setAttribute('aria-expanded', 'false');
          sm.closest('.has-submenu')?.classList.remove('open');
        }
      });

      btn.setAttribute('aria-expanded', String(!expanded));
      submenu.hidden = expanded;
      wrap.classList.toggle('open', !expanded);
    });
  });

  /* =================== Drawer (hamburger) =================== */
  const body = document.body;
  const sideMenu = document.getElementById('side-menu');
  const openBtn = document.querySelector('.menu-open');   // hamburger in top bar
  const closeBtn = document.querySelector('.menu-close'); // "×" in drawer
  const backdrop = document.querySelector('.menu-backdrop');

  function openMenu() {
    body.classList.add('menu-open');
    sideMenu?.setAttribute('aria-hidden', 'false');
    openBtn?.setAttribute('aria-expanded', 'true');
    if (backdrop) backdrop.hidden = false;
  }
  function closeMenu() {
    body.classList.remove('menu-open');
    sideMenu?.setAttribute('aria-hidden', 'true');
    openBtn?.setAttribute('aria-expanded', 'false');
    if (backdrop) backdrop.hidden = true;
  }

  if (openBtn) {
    openBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      openMenu();
    });
  }
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  if (backdrop) backdrop.addEventListener('click', closeMenu);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && body.classList.contains('menu-open')) closeMenu();
  });});