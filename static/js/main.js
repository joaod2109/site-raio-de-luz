// ── Dark mode ──────────────────────────────────────────────────────────────────
const root = document.documentElement;
const themeBtn = document.getElementById('themeBtn');
const themeLabel = themeBtn ? themeBtn.querySelector('span:last-child') : null;

function applyTheme(theme) {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  if (themeLabel) themeLabel.textContent = theme === 'dark' ? 'Modo claro' : 'Modo escuro';
}

// Inicializa com o tema salvo (o inline script já aplicou ao <html>, só atualiza o label)
if (themeLabel) {
  themeLabel.textContent = root.getAttribute('data-theme') === 'dark' ? 'Modo claro' : 'Modo escuro';
}

if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });
}

// ── Nav scroll ─────────────────────────────────────────────────────────────────
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 20);
});

// ── Menu mobile ────────────────────────────────────────────────────────────────
const toggle = document.getElementById('navToggle');
const links  = document.getElementById('navLinks');
if (toggle && links) {
  toggle.addEventListener('click', () => links.classList.toggle('open'));
  links.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => links.classList.remove('open'));
  });
}

// ── Fade-in ao rolar ───────────────────────────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .evento-item, .value-card, .mission-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});
