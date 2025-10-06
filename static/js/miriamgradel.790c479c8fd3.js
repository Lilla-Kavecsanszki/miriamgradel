// static/js/miriamgradel.js
document.addEventListener('DOMContentLoaded', function () {
  // Submenu toggle
  const toggles = document.querySelectorAll('.menu-toggle');
  toggles.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const parent = btn.closest('.has-submenu');
      const submenu = parent ? parent.querySelector('.submenu') : null;
      if (!submenu) return;

      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      submenu.hidden = expanded;
      parent.classList.toggle('open', !expanded);
    });
  });

  // Mobile "☰" scroll-to-top action
  const menuOpenBtn = document.querySelector('.menu-open');
  if (menuOpenBtn) {
    menuOpenBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Optional: mobile "Contact" button
  const contactBtn = document.querySelector('.mobile-contact');
  if (contactBtn) {
    contactBtn.addEventListener('click', () => {
      window.location.href = '#contact'; // change target as needed
    });
  }
});
