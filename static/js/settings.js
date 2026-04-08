(function () {
  var THEME_KEY  = 'sarah-hub-theme';
  var ACCENT_KEY = 'sarah-hub-accent';
  var BG_KEY     = 'sarah-hub-bg';

  function apply(theme, accent, bg) {
    document.documentElement.setAttribute('data-theme',  theme);
    document.documentElement.setAttribute('data-accent', accent);
    document.documentElement.setAttribute('data-bg',     bg);
  }

  // Apply saved preferences on every page load
  var theme  = localStorage.getItem(THEME_KEY)  || 'dark';
  var accent = localStorage.getItem(ACCENT_KEY) || 'amber';
  var bg     = localStorage.getItem(BG_KEY)     || 'dark';
  apply(theme, accent, bg);

  window.SarahSettings = {
    setTheme: function (t) {
      localStorage.setItem(THEME_KEY, t);
      apply(t, localStorage.getItem(ACCENT_KEY) || 'amber', localStorage.getItem(BG_KEY) || 'dark');
      document.querySelectorAll('.theme-option').forEach(function (el) {
        el.classList.toggle('active', el.dataset.theme === t);
      });
    },
    setAccent: function (a) {
      localStorage.setItem(ACCENT_KEY, a);
      apply(localStorage.getItem(THEME_KEY) || 'dark', a, localStorage.getItem(BG_KEY) || 'dark');
      document.querySelectorAll('.accent-swatch').forEach(function (el) {
        el.classList.toggle('active', el.dataset.accent === a);
      });
    },
    setBg: function (b) {
      localStorage.setItem(BG_KEY, b);
      apply(localStorage.getItem(THEME_KEY) || 'dark', localStorage.getItem(ACCENT_KEY) || 'amber', b);
      document.querySelectorAll('.bg-swatch').forEach(function (el) {
        el.classList.toggle('active', el.dataset.bg === b);
      });
    },
    current: function () {
      return {
        theme:  localStorage.getItem(THEME_KEY)  || 'dark',
        accent: localStorage.getItem(ACCENT_KEY) || 'amber',
        bg:     localStorage.getItem(BG_KEY)     || 'dark',
      };
    },
  };
})();
