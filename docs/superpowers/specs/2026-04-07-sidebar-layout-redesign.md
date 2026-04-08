# Sidebar Layout Redesign — Design Spec
**Date:** 2026-04-07
**Status:** Approved

## Overview

Redesign the site layout with a collapsible icon sidebar replacing the current top nav, a new hero home page with profile photo, a new `/skills` page, a new `/resume` page, and an updated settings page that supports background color switching in addition to accent color.

## Scope

**Files changed:**
- `templates/base.html` — replace top nav with sidebar
- `static/css/style.css` — sidebar styles, remove top-nav styles, add new theme background variables
- `static/js/settings.js` — add background color picker logic
- `templates/home.html` — hero page with profile photo, name, subtitle, CTA buttons
- `templates/skills.html` — new page: tech skills + workshops
- `templates/resume.html` — new page: education, certifications, languages
- `templates/settings.html` — add background color swatches
- `app.py` — add `/skills` and `/resume` routes
- `static/images/sarah.jpg` — profile photo (copy from local Photos library)

No DynamoDB changes. No new tables.

## Design

### Sidebar

A fixed left sidebar present on every page via `base.html`.

**Collapsed state (default):** 56px wide. Shows emoji icons only, centered. No text visible.

**Expanded state (hover):** 200px wide. Smooth CSS transition (`width 0.25s ease`). Shows icon + label side by side.

**Items (in order):**
| Icon | Label | Route |
|------|-------|-------|
| 🏠 | Home | `/` |
| ⏳ | Timeline | `/timeline` |
| 🛠 | Projects | `/projects` |
| 💡 | Skills | `/skills` |
| 🎓 | Resume | `/resume` |
| 🌅 | Sunsets | `/sunsets` |
| 📚 | Books | `/books` |
| 🎮 | Hobbies | `/hobbies` |
| 👨‍👩‍👧 | Family | `/family` |
| 💬 | Contact | `/contact` |
| ⚙️ | Settings | `/settings` |

The active page link is highlighted in `--accent` color. All others use `--text-secondary`.

The 🌍 visit counter pill moves from the top nav into the sidebar, below the Settings link.

**Mobile (≤768px):** Sidebar hides. A fixed bottom tab bar shows the 5 most-used icons: 🏠 🛠 💡 🎓 ⚙️.

**Layout shift:** `<main>` gets `margin-left: 56px` so content is never hidden behind the sidebar. On sidebar hover, `<main>` does NOT shift — the expanded sidebar overlays content (like the Adam portfolio).

### Home page (`/`)

**Hero section:**
- Circular profile photo (Sarah's photo, `static/images/sarah.jpg`), 140px diameter
- `Hi, I'm Sarah Chidzanga ✦` — large heading
- Typed subtitle: `Integration Engineering Intern at Jamf` (CSS animation, types and loops)
- Bio text: "Student builder from MCRI, Vic Falls. Sunset chaser, reader, and proud family person."
- CTA buttons: `🛠 Projects`, `💡 Skills`, `🌅 Sunsets`

**Guestbook section** stays below the hero (unchanged from current `home.html`).

### Skills page (`/skills`)

Two-column layout:

**Left — Tech Skills:**
Each skill has a label row (name left, level right) and a filled bar below. Bar is `height: 6px`, `background: var(--border)`, filled portion uses `background: var(--accent)`, `border-radius: 3px`.

| Skill | Level label | Bar fill |
|-------|------------|----------|
| Swift | Intermediate / Advanced | 75% |
| HTML | Advanced | 85% |
| Git | Intermediate | 55% |
| CSS | Beginner | 30% |
| Python | Beginner | 25% |
| Bash | Beginner | 20% |

No percentage numbers shown — bars only.

**Right — Workshops:**
Pill/tag style cards with accent left-border:
- Jamf 100 & 170
- Jira & Confluence (Atlassian)
- GitHub
- Software Development Life Cycle
- Terminal

### Resume page (`/resume`)

Two-column layout:

**Left column — Education + Certifications:**

Education (timeline style, newest first):
- MCRI (Mobility & Cloud Research Institute) — February 2025
- Mosi oa Tunya High School — 2023–2024 (A-Level)
- Mkhosana Adventist Secondary School — 2022 (O-Level)

Certifications (list with ✦ bullet):
- App Development with Swift — Associate (Certiport, Sep 4, 2025)
- App Development with Swift — Certified User (Certiport, Dec 15, 2025)
- Jamf Certified Associate — Jamf Pro (Nov 13, 2025)
- Jamf Certified Associate — Jamf Protect (Jan 16, 2026)
- Mastering Self-Motivation (LinkedIn Learning, Sep 25, 2025)
- Software Development Life Cycle / SDLC (LinkedIn Learning, Mar 24, 2025)

**Right column — Languages:**
Same bar style as tech skills. No percentage numbers — bars only.

| Language | Level label | Bar fill |
|----------|------------|----------|
| Shona | Native | 96% |
| English | Fluent | 96% |
| Ndebele | Conversational | 60% |
| French | Beginner | 20% |

### Settings page (`/settings`)

Add a **Background** section above the existing accent color section.

Background options (circle swatches, same interaction pattern as accent):

| Name | `data-bg` value | Background color |
|------|----------------|-----------------|
| Dark | `dark` | `#111111` |
| Deep Blue | `deep-blue` | `#0f1929` |
| Pearl | `pearl` | `#F8F6FA` |
| Sage | `sage` | `#E8EFE8` |
| Midnight | `midnight` | `#1e1b2e` |

`settings.js` writes `data-bg` on `<html>` and saves to `localStorage` as `bg`. On page load, `settings.js` reads `bg` from localStorage and applies it. CSS defines `[data-bg="deep-blue"]` etc. blocks that override `--bg-primary`, `--bg-secondary`, `--bg-card`, `--border`.

The existing `data-theme` system stays — `data-bg` is an additional independent attribute.

## What Stays the Same

- All existing routes and templates (timeline, projects, sunsets, books, hobbies, family, contact)
- DynamoDB tables and queries
- HTMX partials (likes, comments, visits)
- Puzzle feature
- Accent color system (`data-accent`)
- All existing theme variables

## Out of Scope

- Admin panel
- Animated skill bars on scroll
- CV/PDF download
- Community service section (can be added later)
- Soft skills section (can be added later)
