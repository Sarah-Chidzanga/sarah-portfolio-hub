# Sidebar Layout Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the top nav with a collapsible icon sidebar, add a hero home page with profile photo, add `/skills` and `/resume` pages, and add background color switching to settings.

**Architecture:** All layout changes go through `base.html` (sidebar HTML) and `style.css` (sidebar + bg theme CSS). Two new Flask blueprints (`skills`, `resume`) follow the existing pattern in `routes/`. The settings system gains a `data-bg` attribute on `<html>` alongside the existing `data-theme` and `data-accent` attributes, all managed by `settings.js` via localStorage.

**Tech Stack:** Flask/Jinja2, vanilla CSS (CSS custom properties), vanilla JS, pytest/moto for tests.

---

## File Map

| File | Change |
|------|--------|
| `static/images/sarah.jpg` | Create — profile photo copied from Photos library |
| `static/css/style.css` | Modify — add sidebar styles, bg theme vars, skill bar styles, mobile nav; remove/replace top-nav styles |
| `static/js/settings.js` | Modify — add `setBg` function and load bg on page load |
| `templates/base.html` | Modify — replace top-nav with sidebar + mobile bottom nav |
| `templates/home.html` | Modify — new hero section with photo, typed subtitle, CTA buttons |
| `templates/settings.html` | Modify — add background swatches section |
| `routes/skills.py` | Create — `/skills` route |
| `routes/resume.py` | Create — `/resume` route |
| `templates/skills.html` | Create — skills page template |
| `templates/resume.html` | Create — resume page template |
| `app.py` | Modify — register skills_bp and resume_bp |
| `tests/test_skills.py` | Create — tests for /skills route |
| `tests/test_resume.py` | Create — tests for /resume route |

---

### Task 1: Copy profile photo to static/images/

**Files:**
- Create: `static/images/sarah.jpg`

- [ ] **Step 1: Run baseline tests**

```bash
pytest tests/ -v
```
Expected: all tests pass.

- [ ] **Step 2: Copy the photo**

```bash
cp "/Users/sarah.chidzanga/Pictures/Photos Library.photoslibrary/resources/derivatives/5/54CA7E73-F903-46CA-9E0D-C687F89C379D_1_105_c.jpeg" static/images/sarah.jpg
```

- [ ] **Step 3: Verify**

```bash
ls -lh static/images/sarah.jpg
```
Expected: file exists, size > 0.

- [ ] **Step 4: Commit**

```bash
git add static/images/sarah.jpg
git commit -m "feat: add profile photo for hero section"
```

---

### Task 2: Add sidebar CSS, bg theme variables, skill bar styles to style.css

**Files:**
- Modify: `static/css/style.css`

- [ ] **Step 1: Run tests**

```bash
pytest tests/ -v
```
Expected: all pass.

- [ ] **Step 2: Replace the `.top-nav` block and add all new CSS**

In `static/css/style.css`, find the `/* ── Navigation ── */` block (lines 62–103) and replace it entirely with the following. Then append the new sections at the end of the file.

Replace lines 62–103 (the entire `.top-nav`, `.nav-brand`, `.nav-links`, `.nav-links a`, `.nav-links a:hover`, `.visit-pill` block):

```css
/* ── Sidebar ───────────────────────────────────────────────── */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 56px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1rem 0;
  z-index: 200;
  overflow: hidden;
  transition: width 0.25s ease;
}

.sidebar:hover {
  width: 200px;
}

.sidebar-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 0.75rem;
  margin-bottom: 1rem;
  width: 200px;
  flex-shrink: 0;
}

.sidebar-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  border: 2px solid var(--accent);
}

.sidebar-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.sidebar:hover .sidebar-name { opacity: 1; }

.sidebar-divider {
  width: 100%;
  height: 1px;
  background: var(--border);
  margin-bottom: 0.5rem;
  flex-shrink: 0;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.55rem 0.75rem;
  width: 200px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-decoration: none;
  transition: color 0.2s, background 0.2s;
  border-radius: 0;
  flex-shrink: 0;
  white-space: nowrap;
}

.sidebar-link:hover { color: var(--accent); background: rgba(0,0,0,0.06); }
.sidebar-link.active { color: var(--accent); }

.sidebar-icon { font-size: 1.1rem; flex-shrink: 0; width: 20px; text-align: center; }

.sidebar-label {
  opacity: 0;
  transition: opacity 0.15s ease;
}

.sidebar:hover .sidebar-label { opacity: 1; }

.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
}

.visit-pill {
  font-size: 0.72rem;
  background: rgba(245,158,11,0.12);
  color: var(--accent);
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.15s ease;
  margin: 0.25rem 0.75rem 0.5rem;
}

.sidebar:hover .visit-pill { opacity: 1; }

/* ── Mobile bottom nav ─────────────────────────────────────── */
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  z-index: 200;
  justify-content: space-around;
  align-items: center;
}

@media (max-width: 768px) {
  .sidebar { display: none; }
  .mobile-nav { display: flex; }
  main { margin-left: 0 !important; padding-bottom: 4rem; }
}

.mobile-nav a {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-secondary);
  font-size: 0.6rem;
  gap: 0.1rem;
  padding: 0.25rem 0.5rem;
  text-decoration: none;
}

.mobile-nav a.active { color: var(--accent); }
.mobile-nav a span:first-child { font-size: 1.3rem; }
```

Also replace the `.visit-pill` rule that was at line 96–103 (it's now included in the sidebar block above, so remove the old standalone one if it still exists after the replacement).

- [ ] **Step 3: Append bg theme variables and skill bar CSS at the end of style.css**

Add at the very end of `static/css/style.css`:

```css
/* ── Background themes (data-bg) ───────────────────────────── */
[data-bg="dark"] {
  --bg-primary:   #111111;
  --bg-secondary: #1a1a1a;
  --bg-card:      #222222;
  --text-primary: #f0ece3;
  --text-secondary:#a89a8a;
  --border:       #2a2a2a;
  --shadow:       0 2px 12px rgba(0,0,0,0.4);
}

[data-bg="deep-blue"] {
  --bg-primary:   #0f1929;
  --bg-secondary: #162236;
  --bg-card:      #1e2d42;
  --text-primary: #e8f0fe;
  --text-secondary:#8aaccc;
  --border:       #1e3050;
  --shadow:       0 2px 12px rgba(0,0,0,0.5);
}

[data-bg="pearl"] {
  --bg-primary:   #F8F6FA;
  --bg-secondary: #EEEcF4;
  --bg-card:      #FFFFFF;
  --text-primary: #2A1A3A;
  --text-secondary:#6A5A7A;
  --border:       #DCD8E8;
  --shadow:       0 2px 12px rgba(42,26,58,0.08);
}

[data-bg="sage"] {
  --bg-primary:   #E8EFE8;
  --bg-secondary: #D8E4D8;
  --bg-card:      #F4F8F4;
  --text-primary: #1F2D1F;
  --text-secondary:#6B6D43;
  --border:       #C4D4C4;
  --shadow:       0 2px 12px rgba(31,45,31,0.1);
}

[data-bg="midnight"] {
  --bg-primary:   #1e1b2e;
  --bg-secondary: #2a2640;
  --bg-card:      #332f4a;
  --text-primary: #e8e4f8;
  --text-secondary:#9e99c2;
  --border:       #3a3555;
  --shadow:       0 2px 12px rgba(0,0,0,0.45);
}

/* ── Skill bars ────────────────────────────────────────────── */
.skill-bar-wrap {
  margin-bottom: 1rem;
}

.skill-bar-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
}

.skill-bar-label span:last-child {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.skill-bar-track {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.skill-bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
}

/* ── Workshop tags ─────────────────────────────────────────── */
.workshop-tag {
  display: block;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
  font-size: 0.9rem;
  color: var(--text-primary);
}

/* ── Resume timeline ───────────────────────────────────────── */
.edu-item {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
}

.edu-item:last-child { border-bottom: none; }

.edu-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.edu-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.cert-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.9rem;
}

.cert-item:last-child { border-bottom: none; }

.cert-bullet {
  color: var(--accent);
  flex-shrink: 0;
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/ -v
```
Expected: all pass (CSS changes don't affect Python tests).

- [ ] **Step 5: Commit**

```bash
git add static/css/style.css
git commit -m "feat: add sidebar CSS, bg theme variables, skill bar and resume styles"
```

---

### Task 3: Update base.html — replace top-nav with sidebar

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Replace the entire contents of templates/base.html**

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="amber" data-bg="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Sarah Chidzanga{% endblock %}</title>
  <meta property="og:title" content="Sarah Chidzanga — Portfolio">
  <meta property="og:description" content="Integration Engineering Intern at Jamf. Sunsets, code, and stories from Zimbabwe.">
  <meta property="og:image" content="https://7bhqlex2ivl72hlnbmtayjgzya0vdflr.lambda-url.us-east-1.on.aws/static/images/og.png">
  <meta property="og:url" content="https://7bhqlex2ivl72hlnbmtayjgzya0vdflr.lambda-url.us-east-1.on.aws/">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <script src="https://unpkg.com/htmx.org@1.9.10" defer></script>
</head>
<body>

  <nav class="sidebar">
    <div class="sidebar-profile">
      <img src="{{ url_for('static', filename='images/sarah.jpg') }}" alt="Sarah" class="sidebar-avatar">
      <span class="sidebar-name">Sarah C.</span>
    </div>
    <div class="sidebar-divider"></div>

    <a href="/"          class="sidebar-link {% if request.path == '/' %}active{% endif %}">
      <span class="sidebar-icon">🏠</span><span class="sidebar-label">Home</span>
    </a>
    <a href="/timeline"  class="sidebar-link {% if request.path == '/timeline' %}active{% endif %}">
      <span class="sidebar-icon">⏳</span><span class="sidebar-label">Timeline</span>
    </a>
    <a href="/projects"  class="sidebar-link {% if request.path == '/projects' %}active{% endif %}">
      <span class="sidebar-icon">🛠</span><span class="sidebar-label">Projects</span>
    </a>
    <a href="/skills"    class="sidebar-link {% if request.path == '/skills' %}active{% endif %}">
      <span class="sidebar-icon">💡</span><span class="sidebar-label">Skills</span>
    </a>
    <a href="/resume"    class="sidebar-link {% if request.path == '/resume' %}active{% endif %}">
      <span class="sidebar-icon">🎓</span><span class="sidebar-label">Resume</span>
    </a>
    <a href="/sunsets"   class="sidebar-link {% if request.path.startswith('/sunset') %}active{% endif %}">
      <span class="sidebar-icon">🌅</span><span class="sidebar-label">Sunsets</span>
    </a>
    <a href="/books"     class="sidebar-link {% if request.path == '/books' %}active{% endif %}">
      <span class="sidebar-icon">📚</span><span class="sidebar-label">Books</span>
    </a>
    <a href="/hobbies"   class="sidebar-link {% if request.path == '/hobbies' %}active{% endif %}">
      <span class="sidebar-icon">🎮</span><span class="sidebar-label">Hobbies</span>
    </a>
    <a href="/family"    class="sidebar-link {% if request.path == '/family' %}active{% endif %}">
      <span class="sidebar-icon">👨‍👩‍👧</span><span class="sidebar-label">Family</span>
    </a>
    <a href="/contact"   class="sidebar-link {% if request.path == '/contact' %}active{% endif %}">
      <span class="sidebar-icon">💬</span><span class="sidebar-label">Contact</span>
    </a>

    <div class="sidebar-footer">
      <a href="/settings" class="sidebar-link {% if request.path == '/settings' %}active{% endif %}">
        <span class="sidebar-icon">⚙️</span><span class="sidebar-label">Settings</span>
      </a>
      <div hx-get="/visits/global"
           hx-trigger="load"
           hx-swap="outerHTML">
        <span class="visit-pill">🌍 ...</span>
      </div>
    </div>
  </nav>

  <!-- Mobile bottom nav -->
  <nav class="mobile-nav">
    <a href="/"        class="{% if request.path == '/' %}active{% endif %}">
      <span>🏠</span><span>Home</span>
    </a>
    <a href="/projects" class="{% if request.path == '/projects' %}active{% endif %}">
      <span>🛠</span><span>Projects</span>
    </a>
    <a href="/skills"   class="{% if request.path == '/skills' %}active{% endif %}">
      <span>💡</span><span>Skills</span>
    </a>
    <a href="/resume"   class="{% if request.path == '/resume' %}active{% endif %}">
      <span>🎓</span><span>Resume</span>
    </a>
    <a href="/settings" class="{% if request.path == '/settings' %}active{% endif %}">
      <span>⚙️</span><span>Settings</span>
    </a>
  </nav>

  <main style="margin-left: 56px;">
    {% block content %}{% endblock %}
  </main>

  <script src="{{ url_for('static', filename='js/settings.js') }}"></script>
  <script src="{{ url_for('static', filename='js/animations.js') }}"></script>
</body>
</html>
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/ -v
```
Expected: all pass — `test_home_returns_200` checks for `b'Sarah'` which is still present.

- [ ] **Step 3: Commit**

```bash
git add templates/base.html
git commit -m "feat: replace top nav with collapsible icon sidebar"
```

---

### Task 4: Update home.html — hero with profile photo and typed subtitle

**Files:**
- Modify: `templates/home.html`

- [ ] **Step 1: Replace the hero section in templates/home.html**

Find the existing `<section class="hero">` block (lines 5–16) and replace it with:

```html
<section class="hero" style="display:flex; gap:2.5rem; align-items:center; flex-wrap:wrap; padding:3rem 0 2rem; border-bottom:1px solid var(--border); margin-bottom:2.5rem;">
  <img src="{{ url_for('static', filename='images/sarah.jpg') }}"
       alt="Sarah Chidzanga"
       style="width:140px; height:140px; border-radius:50%; object-fit:cover; border:3px solid var(--accent); flex-shrink:0;">
  <div>
    <h1 style="font-size:2.5rem; margin-bottom:0.25rem;">Hi, I'm <span style="color:var(--accent);">Sarah Chidzanga</span> ✦</h1>
    <p id="typed-subtitle" style="font-size:1.1rem; color:var(--accent); margin-bottom:0.75rem; min-height:1.6em;"></p>
    <p style="color:var(--text-secondary); max-width:520px; margin-bottom:1.5rem;">
      Student builder from MCRI, Vic Falls. Sunset chaser, reader, and proud family person.
    </p>
    <div style="display:flex; gap:0.75rem; flex-wrap:wrap;">
      <a href="/projects" class="like-btn" style="text-decoration:none;">🛠 Projects</a>
      <a href="/skills"   class="like-btn" style="text-decoration:none;">💡 Skills</a>
      <a href="/sunsets"  class="like-btn" style="text-decoration:none;">🌅 Sunsets</a>
    </div>
  </div>
</section>

<script>
  (function() {
    var text = 'Integration Engineering Intern at Jamf';
    var el = document.getElementById('typed-subtitle');
    var i = 0;
    function type() {
      if (i <= text.length) {
        el.textContent = text.slice(0, i) + (i < text.length ? '|' : '');
        i++;
        setTimeout(type, 55);
      }
    }
    type();
  })();
</script>
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/test_home.py -v
```
Expected: all 4 tests pass (`test_home_returns_200` still finds `b'Sarah'`).

- [ ] **Step 3: Commit**

```bash
git add templates/home.html
git commit -m "feat: new hero section with profile photo and typed subtitle"
```

---

### Task 5: Update settings.js — add background color picker

**Files:**
- Modify: `static/js/settings.js`

- [ ] **Step 1: Replace the entire contents of static/js/settings.js**

```javascript
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
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/ -v
```
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add static/js/settings.js
git commit -m "feat: add setBg to settings.js for background color switching"
```

---

### Task 6: Update settings.html — add background swatches

**Files:**
- Modify: `templates/settings.html`

- [ ] **Step 1: Replace the entire contents of templates/settings.html**

```html
{% extends "base.html" %}
{% block title %}Settings — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Settings</h1>
<p class="section-subtitle">Customise how the site looks for you. Saved in your browser.</p>

<div class="settings-section">
  <h3>🖼 Background</h3>
  <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 0.75rem;">Background colour</p>
  <div class="accent-options" style="margin-bottom:1.25rem;">
    <div class="accent-swatch bg-swatch" data-bg="dark"
         style="background:#111111;"
         onclick="SarahSettings.setBg('dark')" title="Dark"></div>
    <div class="accent-swatch bg-swatch" data-bg="deep-blue"
         style="background:#0f1929;"
         onclick="SarahSettings.setBg('deep-blue')" title="Deep Blue"></div>
    <div class="accent-swatch bg-swatch" data-bg="midnight"
         style="background:#1e1b2e;"
         onclick="SarahSettings.setBg('midnight')" title="Midnight"></div>
    <div class="accent-swatch bg-swatch" data-bg="pearl"
         style="background:#F8F6FA; border:1px solid var(--border);"
         onclick="SarahSettings.setBg('pearl')" title="Pearl"></div>
    <div class="accent-swatch bg-swatch" data-bg="sage"
         style="background:#E8EFE8;"
         onclick="SarahSettings.setBg('sage')" title="Sage"></div>
  </div>
</div>

<div class="settings-section">
  <h3>🎨 Appearance</h3>

  <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 0.75rem;">Accent Colour</p>
  <div class="accent-options">
    <div class="accent-swatch" data-accent="amber"  style="background:#f59e0b;" onclick="SarahSettings.setAccent('amber')"  title="Amber"></div>
    <div class="accent-swatch" data-accent="rust"   style="background:#ef4444;" onclick="SarahSettings.setAccent('rust')"   title="Rust"></div>
    <div class="accent-swatch" data-accent="violet" style="background:#8b5cf6;" onclick="SarahSettings.setAccent('violet')" title="Violet"></div>
    <div class="accent-swatch" data-accent="sage"   style="background:#10b981;" onclick="SarahSettings.setAccent('sage')"   title="Sage"></div>
    <div class="accent-swatch" data-accent="blue"   style="background:#3b82f6;" onclick="SarahSettings.setAccent('blue')"   title="Blue"></div>
    <div class="accent-swatch" data-accent="rose"   style="background:#CF7D65;" onclick="SarahSettings.setAccent('rose')"   title="Rose"></div>
  </div>

  <p style="margin-top: 1rem; font-size: 0.78rem; color: var(--text-secondary);">
    Each visitor picks their own preference — it doesn't change what others see.
  </p>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function () {
    var c = SarahSettings.current();
    document.querySelectorAll('.theme-option').forEach(function (el) {
      el.classList.toggle('active', el.dataset.theme === c.theme);
    });
    document.querySelectorAll('.accent-swatch:not(.bg-swatch)').forEach(function (el) {
      el.classList.toggle('active', el.dataset.accent === c.accent);
    });
    document.querySelectorAll('.bg-swatch').forEach(function (el) {
      el.classList.toggle('active', el.dataset.bg === c.bg);
    });
  });
</script>
{% endblock %}
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/ -v
```
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add templates/settings.html
git commit -m "feat: add background colour swatches to settings page"
```

---

### Task 7: Create /skills route and template

**Files:**
- Create: `routes/skills.py`
- Create: `templates/skills.html`
- Modify: `app.py`
- Create: `tests/test_skills.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_skills.py`:

```python
import pytest
import os
from moto import mock_aws
import boto3
from tests.conftest import TABLE_SCHEMAS


@pytest.fixture(autouse=True)
def setup_env():
    os.environ.update({
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_REGION': 'us-east-1',
    })


@pytest.fixture
def client():
    with mock_aws():
        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        for schema in TABLE_SCHEMAS:
            ddb.create_table(**schema)
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_skills_returns_200(client):
    resp = client.get('/skills')
    assert resp.status_code == 200


def test_skills_contains_swift(client):
    resp = client.get('/skills')
    assert b'Swift' in resp.data


def test_skills_contains_workshops(client):
    resp = client.get('/skills')
    assert b'Jamf' in resp.data
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_skills.py -v
```
Expected: FAIL — 404 because `/skills` route doesn't exist yet.

- [ ] **Step 3: Create routes/skills.py**

```python
from flask import Blueprint, render_template
from db import track_visit

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills')
def skills():
    track_visit('skills')
    return render_template('skills.html')
```

- [ ] **Step 4: Create templates/skills.html**

```html
{% extends "base.html" %}
{% block title %}Skills — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Skills</h1>
<p class="section-subtitle">Technologies I work with and workshops I've completed.</p>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:2.5rem; flex-wrap:wrap;">

  <!-- Tech Skills -->
  <div>
    <h2 style="font-size:1rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1.25rem;">Tech Skills</h2>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>Swift</span><span>Intermediate / Advanced</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:75%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>HTML</span><span>Advanced</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:85%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>Git</span><span>Intermediate</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:55%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>CSS</span><span>Beginner</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:30%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>Python</span><span>Beginner</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:25%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>Bash</span><span>Beginner</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:20%;"></div></div>
    </div>
  </div>

  <!-- Workshops -->
  <div>
    <h2 style="font-size:1rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1.25rem;">Workshops</h2>
    <div class="workshop-tag">Jamf 100 &amp; 170</div>
    <div class="workshop-tag">Jira &amp; Confluence (Atlassian)</div>
    <div class="workshop-tag">GitHub</div>
    <div class="workshop-tag">Software Development Life Cycle</div>
    <div class="workshop-tag">Terminal</div>
  </div>

</div>
{% endblock %}
```

- [ ] **Step 5: Register skills_bp in app.py**

In `app.py`, inside `create_app()`, add after `from routes.puzzle import puzzle_bp`:

```python
    from routes.skills import skills_bp
```

And add after `app.register_blueprint(puzzle_bp)`:

```python
    app.register_blueprint(skills_bp)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/test_skills.py -v
```
Expected: all 3 pass.

- [ ] **Step 7: Run full test suite**

```bash
pytest tests/ -v
```
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add routes/skills.py templates/skills.html tests/test_skills.py app.py
git commit -m "feat: add /skills page with tech skill bars and workshops"
```

---

### Task 8: Create /resume route and template

**Files:**
- Create: `routes/resume.py`
- Create: `templates/resume.html`
- Modify: `app.py`
- Create: `tests/test_resume.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_resume.py`:

```python
import pytest
import os
from moto import mock_aws
import boto3
from tests.conftest import TABLE_SCHEMAS


@pytest.fixture(autouse=True)
def setup_env():
    os.environ.update({
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_REGION': 'us-east-1',
    })


@pytest.fixture
def client():
    with mock_aws():
        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        for schema in TABLE_SCHEMAS:
            ddb.create_table(**schema)
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_resume_returns_200(client):
    resp = client.get('/resume')
    assert resp.status_code == 200


def test_resume_contains_education(client):
    resp = client.get('/resume')
    assert b'MCRI' in resp.data


def test_resume_contains_certifications(client):
    resp = client.get('/resume')
    assert b'Swift' in resp.data


def test_resume_contains_languages(client):
    resp = client.get('/resume')
    assert b'Shona' in resp.data
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_resume.py -v
```
Expected: FAIL — 404 because `/resume` doesn't exist yet.

- [ ] **Step 3: Create routes/resume.py**

```python
from flask import Blueprint, render_template
from db import track_visit

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/resume')
def resume():
    track_visit('resume')
    return render_template('resume.html')
```

- [ ] **Step 4: Create templates/resume.html**

```html
{% extends "base.html" %}
{% block title %}Resume — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Resume</h1>
<p class="section-subtitle">Education, certifications, and languages.</p>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:2.5rem; flex-wrap:wrap;">

  <!-- Left: Education + Certifications -->
  <div>
    <h2 style="font-size:1rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1.25rem;">Education</h2>

    <div class="edu-item">
      <div class="edu-title">MCRI — Mobility &amp; Cloud Research Institute</div>
      <div class="edu-date">February 2025 — present</div>
    </div>
    <div class="edu-item">
      <div class="edu-title">Mosi oa Tunya High School</div>
      <div class="edu-date">2023 – 2024 · Advanced Level</div>
    </div>
    <div class="edu-item">
      <div class="edu-title">Mkhosana Adventist Secondary School</div>
      <div class="edu-date">2022 · Ordinary Level</div>
    </div>

    <h2 style="font-size:1rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.05em; margin:2rem 0 1.25rem;">Certifications</h2>

    <div class="cert-item">
      <span class="cert-bullet">✦</span>
      <div>
        <div>App Development with Swift — Associate</div>
        <div style="font-size:0.8rem;color:var(--text-secondary);">Certiport · Sep 4, 2025</div>
      </div>
    </div>
    <div class="cert-item">
      <span class="cert-bullet">✦</span>
      <div>
        <div>App Development with Swift — Certified User</div>
        <div style="font-size:0.8rem;color:var(--text-secondary);">Certiport · Dec 15, 2025</div>
      </div>
    </div>
    <div class="cert-item">
      <span class="cert-bullet">✦</span>
      <div>
        <div>Jamf Certified Associate — Jamf Pro</div>
        <div style="font-size:0.8rem;color:var(--text-secondary);">Jamf · Nov 13, 2025</div>
      </div>
    </div>
    <div class="cert-item">
      <span class="cert-bullet">✦</span>
      <div>
        <div>Jamf Certified Associate — Jamf Protect</div>
        <div style="font-size:0.8rem;color:var(--text-secondary);">Jamf · Jan 16, 2026</div>
      </div>
    </div>
    <div class="cert-item">
      <span class="cert-bullet">✦</span>
      <div>
        <div>Mastering Self-Motivation</div>
        <div style="font-size:0.8rem;color:var(--text-secondary);">LinkedIn Learning · Sep 25, 2025</div>
      </div>
    </div>
    <div class="cert-item">
      <span class="cert-bullet">✦</span>
      <div>
        <div>Software Development Life Cycle / SDLC</div>
        <div style="font-size:0.8rem;color:var(--text-secondary);">LinkedIn Learning · Mar 24, 2025</div>
      </div>
    </div>
  </div>

  <!-- Right: Languages -->
  <div>
    <h2 style="font-size:1rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1.25rem;">Languages</h2>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>Shona</span><span>Native</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:96%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>English</span><span>Fluent</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:96%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>Ndebele</span><span>Conversational</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:60%;"></div></div>
    </div>

    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>French</span><span>Beginner</span></div>
      <div class="skill-bar-track"><div class="skill-bar-fill" style="width:20%;"></div></div>
    </div>
  </div>

</div>
{% endblock %}
```

- [ ] **Step 5: Register resume_bp in app.py**

In `app.py`, add `from routes.resume import resume_bp` after the `from routes.skills import skills_bp` line. Then add the registration inside `create_app()` after `app.register_blueprint(skills_bp)`:

```python
    app.register_blueprint(resume_bp)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/test_resume.py -v
```
Expected: all 4 pass.

- [ ] **Step 7: Run full test suite**

```bash
pytest tests/ -v
```
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add routes/resume.py templates/resume.html tests/test_resume.py app.py
git commit -m "feat: add /resume page with education, certifications, and languages"
```

---

### Task 9: Browser verification

**Files:** No code changes — visual verification only.

- [ ] **Step 1: Start the app (requires AWS credentials in environment)**

```bash
python app.py
```

If running locally without AWS credentials, deploy to prod and verify there instead:
```bash
git push origin main
```

- [ ] **Step 2: Verify sidebar**

Open the site. Check:
- Sidebar shows icons only at 56px wide
- Hovering sidebar expands to ~200px with labels visible
- Active page is highlighted in accent color
- 🌍 visit counter appears at bottom of sidebar on hover

- [ ] **Step 3: Verify home page**

Open `/`. Check:
- Profile photo appears in a circle
- "Hi, I'm Sarah Chidzanga ✦" heading
- Typed subtitle animation plays
- Three CTA buttons

- [ ] **Step 4: Verify skills page**

Open `/skills`. Check:
- Two-column layout (tech skills + workshops)
- Skill bars are filled lines with labels, no percentages
- Workshop items have accent left border

- [ ] **Step 5: Verify resume page**

Open `/resume`. Check:
- Education list (3 items, newest first)
- Certifications list (6 items with ✦ bullets and dates)
- Language bars (4 items, no percentages)

- [ ] **Step 6: Verify settings page**

Open `/settings`. Check:
- Background swatches section at top
- Clicking a background swatch changes the page background immediately
- Preference persists after page refresh
- Accent swatches still work

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: sidebar layout redesign — hero, skills, resume, bg settings complete"
```
