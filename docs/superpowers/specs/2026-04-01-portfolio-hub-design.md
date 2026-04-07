# Sarah's Portfolio Hub — Design Spec

**Date:** 2026-04-01
**Status:** Approved
**Stack:** Flask · HTMX · DynamoDB · AWS Lambda · S3

---

## 1. Overview

A personal + professional portfolio web app for Sarah Chidzanga — Integration Engineering intern at Jamf. The site functions as a "living integration assistant + personal story": it showcases Sarah's technical work (Jamf integration projects, MCRI student apps), her personal life (sunset photography, reading, family), and her professional journey through an interactive timeline.

**Core feel:** Dark and warm — near-black background with amber/orange sunset accent tones. Clean, modern, performance-friendly. Subtle animations throughout (timeline slide-ins, heart bounce on like, comment fade-in).

---

## 2. Navigation & Pages

9 pages, all accessible from a persistent top nav bar.

```
✦ Sarah Chidzanga   Home | Timeline | Projects | Sunsets | Books | Hobbies | Family | Contact | ⚙️   🌍 1,204 visits
```

| Route | Page | Interactive Features |
|---|---|---|
| `/` | Home | Guestbook comments, likes, global visit counter |
| `/timeline` | Timeline | HTMX card expand per milestone |
| `/projects` | Projects list | Filter by category (Jamf / MCRI) |
| `/projects/<slug>` | Project detail | Likes, comments, Living Brief phases |
| `/sunsets` | Sunset gallery | Masonry grid, lightbox, likes, comments |
| `/books` | Books | Read-only list |
| `/hobbies` | Hobbies | Read-only cards, links to Sunsets + Books |
| `/family` | Family | Read-only photos + description |
| `/contact` | Contact | Email, LinkedIn, Slack handle |
| `/settings` | Settings | Appearance (theme + accent colour) |

**Visit counter:** 🌍 shown as an amber pill in the top-right of the nav. Displays the global total (sum of all page visits). Incremented silently on every page load via HTMX.

---

## 3. Settings Page

Appearance-only (no profile section — visitor-facing, no accounts).

**Themes:**
- ☀️ Light
- 🌿 Natural
- 🌙 Dark *(default)*

**Accent colours:** Amber *(default)* · Rust · Violet · Sage · Blue

Preferences stored in `localStorage` — purely frontend, no server calls. Each visitor keeps their own preference. CSS variables swap instantly on change. The default (Dark + Amber) reflects the site's "dark and warm" brand.

---

## 4. Data Models (DynamoDB)

Five tables. All use on-demand (pay-per-request) billing.

### `projects`
| Key | Type | Notes |
|---|---|---|
| `pk` (partition key) | String | URL slug, e.g. `jamf-splunk-integration` |
| `title` | String | Display name |
| `description` | String | Short summary |
| `category` | String | `jamf` or `mcri` |
| `tech_stack` | List | e.g. `["Flask", "Lambda", "Splunk"]` |
| `current_phase` | String | `Discovery` / `Alignment` / `Planning` / `Build` / `Launch` |
| `phases` | Map | Notes per phase (Living Brief style) |
| `like_count` | Number | Atomically incremented |
| `created_at` | String | ISO timestamp |

### `sunset_photos`
| Key | Type | Notes |
|---|---|---|
| `pk` (partition key) | String | e.g. `sunset-vic-falls-01` |
| `s3_url` | String | Full S3 URL to the image |
| `location` | String | e.g. `Victoria Falls` |
| `story` | String | Caption / short personal story |
| `taken_at` | String | Date photo was taken |
| `like_count` | Number | Atomically incremented |
| `created_at` | String | ISO timestamp |

### `books`
| Key | Type | Notes |
|---|---|---|
| `pk` (partition key) | String | e.g. `atomic-habits` |
| `title` | String | Book title |
| `author` | String | Author name |
| `status` | String | `reading` or `read` |
| `reflection` | String | One-line takeaway |

### `comments`
Single table handles all comment types (guestbook, project comments, photo comments).

| Key | Type | Notes |
|---|---|---|
| `pk` (partition key) | String | Parent item: `home`, `project#<slug>`, `photo#<id>` |
| `sk` (sort key) | String | ISO timestamp — enables newest-first sort |
| `author` | String | Visitor's display name |
| `body` | String | Comment text |

Query by `pk` to get all comments for a parent. DynamoDB sorts ascending by default — use `ScanIndexForward=False` in the query to get newest-first order.

### `page_visits`
| Key | Type | Notes |
|---|---|---|
| `pk` (partition key) | String | Page name: `home`, `projects`, `sunsets`, etc. |
| `count` | Number | Atomically incremented via DynamoDB ADD |
| `last_visited` | String | ISO timestamp of most recent visit |

Special row `pk = "global"` holds the total across all pages — shown in the nav bar. Every page visit performs two atomic ADD operations in parallel: one on the page-specific row and one on `global`.

**Photo storage:** Images uploaded to S3 bucket `sarah-portfolio-photos`. The `s3_url` in DynamoDB points to the public S3 URL.

---

## 5. Flask App Structure

```
sarah-portfolio-hub/
├── app.py                  # Flask app factory, blueprint registration
├── lambda_handler.py       # AWS Lambda entry point (Mangum adapter)
├── db.py                   # DynamoDB helpers: get, put, increment, query
├── requirements.txt        # flask, mangum, boto3
├── package.sh              # Builds deployment .zip for Lambda upload
├── routes/
│   ├── home.py             # /, guestbook, likes
│   ├── timeline.py         # /timeline, HTMX card expand
│   ├── projects.py         # /projects, /projects/<slug>
│   ├── sunsets.py          # /sunsets, lightbox, likes, comments
│   ├── books.py            # /books
│   ├── hobbies.py          # /hobbies
│   ├── family.py           # /family
│   ├── contact.py          # /contact
│   └── settings.py         # /settings
├── templates/
│   ├── base.html           # Nav bar, visit counter, theme CSS vars, HTMX CDN
│   ├── home.html
│   ├── timeline.html
│   ├── projects/
│   │   ├── list.html
│   │   └── detail.html
│   ├── sunsets.html
│   ├── books.html
│   ├── hobbies.html
│   ├── family.html
│   ├── contact.html
│   ├── settings.html
│   └── partials/           # HTMX-swappable HTML fragments
│       ├── comment_list.html
│       ├── like_button.html
│       └── visit_count.html
└── static/
    ├── css/style.css       # CSS custom properties for themes + accent colours
    ├── js/settings.js      # localStorage theme/accent logic
    └── js/animations.js    # Timeline slide-in, heart bounce (vanilla JS)
```

### Request flow (full page)
```
Browser → API Gateway → Lambda (Mangum converts event to WSGI) → Flask route → db.py → DynamoDB → Jinja2 template → HTML response
```

### HTMX interaction flow (e.g. like button)
```
1. Visitor clicks ❤
2. HTMX sends POST /like/project/<slug>
3. Flask increments DynamoDB like_count (atomic ADD)
4. Flask returns partials/like_button.html fragment
5. HTMX swaps the button in-place — count updates, heart bounces (CSS keyframe)
```

### Key design rules
- `db.py` is the only file that imports `boto3` — all routes call helpers from it
- `templates/partials/` fragments are the only templates Flask returns for HTMX requests
- Theme + accent colour are 100% frontend (localStorage + CSS variables) — no server involvement
- Visit counts are incremented on page load using `hx-trigger="load"` on a hidden element in `base.html`

---

## 6. AWS Console Deployment

All steps performed through the AWS browser UI — no CLI required.

### Deployment order

| Step | Service | Action |
|---|---|---|
| 1 | S3 | Create bucket `sarah-portfolio-photos`, allow public reads, upload photos |
| 2 | DynamoDB | Create 5 tables (`projects`, `sunset_photos`, `books`, `comments`, `page_visits`) with on-demand billing |
| 3 | IAM | Create role `sarah-portfolio-lambda-role` with `AmazonDynamoDBFullAccess`, `AmazonS3ReadOnlyAccess`, `AWSLambdaBasicExecutionRole` |
| 4 | Lambda | Create function (Python 3.12), attach IAM role, upload `.zip`, set handler to `lambda_handler.handler`, memory 256 MB, timeout 30s |
| 5 | API Gateway | Create HTTP API, integrate with Lambda, add route `ANY /{proxy+}`, deploy to stage `prod` |
| 6 | Custom domain | Optional — Route 53 domain + ACM SSL cert + API Gateway custom domain mapping |

### Re-deploying after code changes
Run `package.sh` locally → produces `app.zip` → Lambda console → Upload from → .zip file. No CLI needed.

---

## 7. Content Sections Detail

### Timeline
Milestones: MCRI Vic Falls (student era) → Jamf internship (present) → Future goals.
Each item shows as a card on the timeline. Clicking expands a detail panel via HTMX (no page reload) showing: description, what Sarah learned, links.

### Projects — Living Brief
Each project has 5 phases: Discovery → Alignment → Planning → Build → Launch.
The `current_phase` field drives a progress indicator on the detail page. The `phases` map holds notes for each completed phase — updating as the project moves forward.

### Sunset Gallery
Masonry grid layout. Clicking a photo opens a lightbox overlay showing the full image, location, and story. Each photo has a like button and comment section within the lightbox overlay (no separate page needed).

### Guestbook (Home)
Comment section at the bottom of the Home page. Visitors enter their name and a message. Newest comments shown first. No authentication — name field is freeform.

---

## 8. Future Features

### Puzzle Piece Shapes
Currently puzzle tiles are plain rectangles. Two planned enhancements:

**Phase 1 — Shape presets:** Add a shape selector to the puzzle difficulty screen. Options: Classic (rectangles), Diamond (tiles rotated 45°), Hexagon (honeycomb grid). Implemented via CSS `clip-path` on each tile.

**Phase 2 — Real jigsaw pieces:** Procedurally generate SVG clip-paths with interlocking tabs and blanks, so adjacent pieces fit together like a real jigsaw. Each edge (top/right/bottom/left) is randomly assigned tab or blank at puzzle generation time, with the neighbouring piece getting the complementary shape.

---

## 9. Out of Scope

- User authentication / login
- Admin panel for managing content (content managed directly in DynamoDB console or via seed scripts)
- Email notifications for new comments
- Search functionality
- RSS feed
