(function () {
  var THEME_KEY = 'sarah-hub-theme';
  var ACCENT_KEY = 'sarah-hub-accent';

  function apply(theme, accent) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-accent', accent);
  }

  // Apply saved preferences on every page load
  var theme = localStorage.getItem(THEME_KEY) || 'dark';
  var accent = localStorage.getItem(ACCENT_KEY) || 'amber';
  apply(theme, accent);

  // Expose for settings page buttons
  window.SarahSettings = {
    setTheme: function (t) {
      localStorage.setItem(THEME_KEY, t);
      apply(t, localStorage.getItem(ACCENT_KEY) || 'amber');
      // Update active state on buttons
      document.querySelectorAll('.theme-option').forEach(function (el) {
        el.classList.toggle('active', el.dataset.theme === t);
      });
    },
    setAccent: function (a) {
      localStorage.setItem(ACCENT_KEY, a);
      apply(localStorage.getItem(THEME_KEY) || 'dark', a);
      document.querySelectorAll('.accent-swatch').forEach(function (el) {
        el.classList.toggle('active', el.dataset.accent === a);
      });
    },
    current: function () {
      return {
        theme: localStorage.getItem(THEME_KEY) || 'dark',
        accent: localStorage.getItem(ACCENT_KEY) || 'amber',
      };
    },
  };
})();
