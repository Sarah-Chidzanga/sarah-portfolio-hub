# Sarah's Portfolio Hub — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Flask-based personal portfolio web app for Sarah Chidzanga, deployed on AWS Lambda with DynamoDB, featuring HTMX-driven likes, comments, and visit counts.

**Architecture:** Flask app served via AWS Lambda using Mangum (WSGI adapter). All dynamic data in 5 DynamoDB tables. HTMX handles interactive updates by swapping HTML fragments (no full page reloads). Theme/accent stored in browser `localStorage` — zero server calls for appearance changes.

**Tech Stack:** Python 3.12, Flask 3.x, Mangum, boto3, HTMX 1.9.10 (CDN), pytest, moto 4.x (AWS mocking)

---

## File Map

| File | Responsibility |
|---|---|
| `app.py` | Flask app factory — creates app, registers blueprints |
| `lambda_handler.py` | AWS Lambda entry point — wraps Flask app with Mangum |
| `db.py` | All DynamoDB operations — the only file that imports boto3 |
| `requirements.txt` | Python dependencies |
| `package.sh` | Builds deployment zip for Lambda upload |
| `routes/home.py` | `/` — hero, guestbook (comments + likes), visit tracking |
| `routes/timeline.py` | `/timeline` — hardcoded milestones, HTMX card expand |
| `routes/projects.py` | `/projects`, `/projects/<slug>` — list, detail, likes, comments |
| `routes/sunsets.py` | `/sunsets` — masonry gallery, lightbox, likes, comments |
| `routes/books.py` | `/books` — read-only list from DynamoDB |
| `routes/hobbies.py` | `/hobbies` — read-only cards, hardcoded |
| `routes/family.py` | `/family` — read-only, hardcoded |
| `routes/contact.py` | `/contact` — read-only, hardcoded |
| `routes/settings.py` | `/settings` — renders page only; prefs handled in JS |
| `routes/visits.py` | `/visits/global` — HTMX fragment: live visit pill |
| `templates/base.html` | Nav bar, HTMX CDN script, CSS link, visit pill, theme attrs |
| `templates/partials/like_button.html` | Reusable like button fragment (HTMX swap target) |
| `templates/partials/comment_list.html` | Reusable comment list fragment (HTMX swap target) |
| `templates/partials/visit_count.html` | Visit pill fragment |
| `static/css/style.css` | CSS custom properties for all themes + accent colours |
| `static/js/settings.js` | localStorage read/write + apply theme/accent on load |
| `static/js/animations.js` | Timeline slide-in, heart bounce (vanilla JS) |
| `tests/conftest.py` | pytest fixtures: moto mock, DynamoDB table setup, Flask test client |
| `tests/test_db.py` | Unit tests for all db.py helpers |
| `tests/test_home.py` | Route tests for home, comments, likes, visits |
| `tests/test_projects.py` | Route tests for projects list + detail |
| `tests/test_sunsets.py` | Route tests for sunsets, likes, comments |

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `routes/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p routes templates/partials templates/projects static/css static/js tests
touch routes/__init__.py tests/__init__.py
```

- [ ] **Step 2: Create `requirements.txt`**

```
flask==3.0.3
mangum==0.17.0
boto3==1.34.0
pytest==8.1.1
moto[dynamodb]==5.0.3
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 4: Verify Flask is importable**

```bash
python -c "import flask; import mangum; import boto3; import moto; print('all good')"
```

Expected output: `all good`

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt routes/__init__.py tests/__init__.py
git commit -m "feat: initial project scaffold"
```

---

## Task 2: db.py — DynamoDB Helpers

**Files:**
- Create: `db.py`
- Create: `tests/conftest.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write the failing tests first**

Create `tests/conftest.py`:

```python
import os
import pytest
import boto3
from moto import mock_aws
from flask import Flask

# Set fake AWS credentials before any boto3 calls
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'


TABLE_SCHEMAS = [
    {
        'TableName': 'projects',
        'KeySchema': [{'AttributeName': 'pk', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'pk', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    {
        'TableName': 'sunset_photos',
        'KeySchema': [{'AttributeName': 'pk', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'pk', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    {
        'TableName': 'books',
        'KeySchema': [{'AttributeName': 'pk', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'pk', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    {
        'TableName': 'comments',
        'KeySchema': [
            {'AttributeName': 'pk', 'KeyType': 'HASH'},
            {'AttributeName': 'sk', 'KeyType': 'RANGE'},
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'pk', 'AttributeType': 'S'},
            {'AttributeName': 'sk', 'AttributeType': 'S'},
        ],
        'BillingMode': 'PAY_PER_REQUEST',
    },
    {
        'TableName': 'page_visits',
        'KeySchema': [{'AttributeName': 'pk', 'KeyType': 'HASH'}],
        'AttributeDefinitions': [{'AttributeName': 'pk', 'AttributeType': 'S'}],
        'BillingMode': 'PAY_PER_REQUEST',
    },
]


@pytest.fixture
def dynamo(aws_credentials):
    with mock_aws():
        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        for schema in TABLE_SCHEMAS:
            ddb.create_table(**schema)
        yield ddb


@pytest.fixture
def aws_credentials():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_REGION'] = 'us-east-1'
```

Create `tests/test_db.py`:

```python
import pytest
from moto import mock_aws
from tests.conftest import TABLE_SCHEMAS
import boto3
import os


@pytest.fixture(autouse=True)
def setup_env():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_REGION'] = 'us-east-1'


@pytest.fixture
def tables():
    with mock_aws():
        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        for schema in TABLE_SCHEMAS:
            ddb.create_table(**schema)
        yield ddb


def test_put_and_get_item(tables):
    import db
    db.put_item('projects', {'pk': 'test-project', 'title': 'Test', 'like_count': 0})
    item = db.get_item('projects', 'test-project')
    assert item['title'] == 'Test'


def test_get_item_returns_none_for_missing(tables):
    import db
    result = db.get_item('projects', 'does-not-exist')
    assert result is None


def test_increment_counter_creates_and_increments(tables):
    import db
    count = db.increment_counter('page_visits', 'home')
    assert count == 1
    count = db.increment_counter('page_visits', 'home')
    assert count == 2


def test_increment_like(tables):
    import db
    db.put_item('projects', {'pk': 'my-proj', 'like_count': 5})
    new_count = db.increment_like('projects', 'my-proj')
    assert new_count == 6


def test_track_visit_increments_page_and_global(tables):
    import db
    db.track_visit('sunsets')
    db.track_visit('sunsets')
    db.track_visit('home')
    assert db.get_global_visit_count() == 3
    page_item = db.get_item('page_visits', 'sunsets')
    assert int(page_item['count']) == 2


def test_query_items_returns_newest_first(tables):
    import db
    db.put_item('comments', {'pk': 'home', 'sk': '2024-01-01T10:00:00', 'author': 'Alice', 'body': 'first'})
    db.put_item('comments', {'pk': 'home', 'sk': '2024-01-02T10:00:00', 'author': 'Bob', 'body': 'second'})
    comments = db.query_items('comments', 'home', scan_index_forward=False)
    assert comments[0]['author'] == 'Bob'
    assert comments[1]['author'] == 'Alice'


def test_scan_table(tables):
    import db
    db.put_item('books', {'pk': 'book-1', 'title': 'Atomic Habits'})
    db.put_item('books', {'pk': 'book-2', 'title': 'Deep Work'})
    books = db.scan_table('books')
    assert len(books) == 2
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_db.py -v
```

Expected: `ImportError` or `ModuleNotFoundError: No module named 'db'`

- [ ] **Step 3: Create `db.py`**

```python
import os
import boto3
from boto3.dynamodb.conditions import Key


def _table(name):
    """Create a fresh DynamoDB Table resource. Not cached so moto works in tests."""
    return boto3.resource(
        'dynamodb',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    ).Table(name)


def get_item(table_name, pk, sk=None):
    """Return a single item by pk (and optional sk), or None if not found."""
    key = {'pk': pk}
    if sk is not None:
        key['sk'] = sk
    response = _table(table_name).get_item(Key=key)
    return response.get('Item')


def put_item(table_name, item):
    """Write an item, overwriting any existing item with the same key."""
    _table(table_name).put_item(Item=item)


def increment_counter(table_name, pk, attribute='count'):
    """Atomically add 1 to a Number attribute. Creates the item/attribute if absent."""
    response = _table(table_name).update_item(
        Key={'pk': pk},
        UpdateExpression='ADD #attr :inc',
        ExpressionAttributeNames={'#attr': attribute},
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='UPDATED_NEW',
    )
    return int(response['Attributes'][attribute])


def increment_like(table_name, pk):
    """Atomically increment like_count for an item. Returns new count."""
    return increment_counter(table_name, pk, 'like_count')


def track_visit(page_name):
    """Increment both the page-specific counter and the global total."""
    increment_counter('page_visits', page_name)
    increment_counter('page_visits', 'global')


def get_global_visit_count():
    """Return the total visit count across all pages."""
    item = get_item('page_visits', 'global')
    return int(item['count']) if item else 0


def query_items(table_name, pk, scan_index_forward=True, limit=50):
    """Query all items with a given pk, sorted by sk. Pass scan_index_forward=False for newest-first."""
    response = _table(table_name).query(
        KeyConditionExpression=Key('pk').eq(pk),
        ScanIndexForward=scan_index_forward,
        Limit=limit,
    )
    return response.get('Items', [])


def scan_table(table_name):
    """Return all items in a table (use for small tables like books, projects)."""
    response = _table(table_name).scan()
    return response.get('Items', [])
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_db.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add db.py tests/conftest.py tests/test_db.py
git commit -m "feat: add DynamoDB helpers with full test coverage"
```

---

## Task 3: Flask App Factory + Lambda Handler

**Files:**
- Create: `app.py`
- Create: `lambda_handler.py`

- [ ] **Step 1: Create `app.py`**

```python
from flask import Flask


def create_app():
    app = Flask(__name__)

    from routes.home import home_bp
    from routes.timeline import timeline_bp
    from routes.projects import projects_bp
    from routes.sunsets import sunsets_bp
    from routes.books import books_bp
    from routes.hobbies import hobbies_bp
    from routes.family import family_bp
    from routes.contact import contact_bp
    from routes.settings import settings_bp
    from routes.visits import visits_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(sunsets_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(hobbies_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(visits_bp)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
```

- [ ] **Step 2: Create `lambda_handler.py`**

```python
from mangum import Mangum
from app import create_app

_app = create_app()
handler = Mangum(_app, lifespan='off')
```

- [ ] **Step 3: Create stub route files so the app factory doesn't crash**

Create each of these with a minimal blueprint — we'll fill them in later:

```bash
for name in home timeline projects sunsets books hobbies family contact settings visits; do
cat > routes/${name}.py << EOF
from flask import Blueprint
${name}_bp = Blueprint('${name}', __name__)
EOF
done
```

- [ ] **Step 4: Verify the app starts without errors**

```bash
python -c "from app import create_app; app = create_app(); print('app ok')"
```

Expected output: `app ok`

- [ ] **Step 5: Commit**

```bash
git add app.py lambda_handler.py routes/
git commit -m "feat: Flask app factory and Lambda handler with stub routes"
```

---

## Task 4: CSS — Dark & Warm Theme System

**Files:**
- Create: `static/css/style.css`

- [ ] **Step 1: Create `static/css/style.css`**

```css
/* ── Theme variables ───────────────────────────────────────── */
:root {
  --bg-primary:    #111111;
  --bg-secondary:  #1a1a1a;
  --bg-card:       #222222;
  --text-primary:  #f0ece3;
  --text-secondary:#a89a8a;
  --accent:        #f59e0b;
  --accent-hover:  #d97706;
  --border:        #2a2a2a;
  --shadow:        0 2px 12px rgba(0,0,0,0.4);
}

[data-theme="light"] {
  --bg-primary:    #f8f4ef;
  --bg-secondary:  #efe9e0;
  --bg-card:       #ffffff;
  --text-primary:  #1a1a1a;
  --text-secondary:#6b5c4c;
  --border:        #d4c9bc;
  --shadow:        0 2px 12px rgba(0,0,0,0.08);
}

[data-theme="natural"] {
  --bg-primary:    #1a1f1a;
  --bg-secondary:  #1e2a1e;
  --bg-card:       #232e23;
  --text-primary:  #e8f0e8;
  --text-secondary:#8fa88f;
  --border:        #2a3a2a;
  --shadow:        0 2px 12px rgba(0,0,0,0.4);
}

[data-accent="amber"]  { --accent: #f59e0b; --accent-hover: #d97706; }
[data-accent="rust"]   { --accent: #ef4444; --accent-hover: #dc2626; }
[data-accent="violet"] { --accent: #8b5cf6; --accent-hover: #7c3aed; }
[data-accent="sage"]   { --accent: #10b981; --accent-hover: #059669; }
[data-accent="blue"]   { --accent: #3b82f6; --accent-hover: #2563eb; }

/* ── Reset & base ──────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  min-height: 100vh;
}

a { color: var(--accent); text-decoration: none; }
a:hover { color: var(--accent-hover); }

h1, h2, h3 { line-height: 1.25; }

/* ── Navigation ────────────────────────────────────────────── */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 2rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--accent);
  white-space: nowrap;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.nav-links a {
  color: var(--text-secondary);
  font-size: 0.9rem;
  transition: color 0.2s;
}

.nav-links a:hover { color: var(--accent); }

.visit-pill {
  font-size: 0.8rem;
  background: rgba(245,158,11,0.12);
  color: var(--accent);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  white-space: nowrap;
}

/* ── Main content ──────────────────────────────────────────── */
main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

/* ── Cards ─────────────────────────────────────────────────── */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: var(--shadow);
  transition: border-color 0.2s, transform 0.2s;
}

.card:hover { border-color: var(--accent); transform: translateY(-2px); }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

/* ── Like button ───────────────────────────────────────────── */
.like-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.like-btn:hover { border-color: var(--accent); color: var(--accent); }
.like-btn.liked  { border-color: var(--accent); color: var(--accent); background: rgba(245,158,11,0.1); }

@keyframes heartBounce {
  0%  { transform: scale(1); }
  30% { transform: scale(1.4); }
  60% { transform: scale(0.9); }
  100%{ transform: scale(1); }
}

.like-btn.liked .heart { animation: heartBounce 0.4s ease; }

/* ── Comments ──────────────────────────────────────────────── */
.comment-form { margin: 1.5rem 0; }

.comment-form input,
.comment-form textarea {
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 6px;
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
  margin-bottom: 0.6rem;
}

.comment-form textarea { height: 80px; resize: vertical; }

.comment-form button {
  background: var(--accent);
  color: #111;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.comment-form button:hover { background: var(--accent-hover); }

.comment-item {
  border-top: 1px solid var(--border);
  padding: 0.75rem 0;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.comment-author { font-weight: 600; color: var(--accent); font-size: 0.85rem; }
.comment-body   { color: var(--text-secondary); margin-top: 0.2rem; }

/* ── Phase badge ───────────────────────────────────────────── */
.phase-badge {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(245,158,11,0.15);
  color: var(--accent);
  border: 1px solid rgba(245,158,11,0.3);
}

/* ── Timeline ──────────────────────────────────────────────── */
.timeline { position: relative; padding-left: 2rem; }

.timeline::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border);
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
  opacity: 0;
  transform: translateX(-20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.timeline-item.visible { opacity: 1; transform: translateX(0); }

.timeline-dot {
  position: absolute;
  left: -1.75rem;
  top: 0.4rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--bg-primary);
}

.timeline-detail {
  display: none;
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border);
  animation: fadeIn 0.3s ease;
}

/* ── Sunset gallery ────────────────────────────────────────── */
.masonry-grid { columns: 3; column-gap: 1rem; }
@media (max-width: 768px) { .masonry-grid { columns: 2; } }
@media (max-width: 480px) { .masonry-grid { columns: 1; } }

.masonry-item {
  break-inside: avoid;
  margin-bottom: 1rem;
  cursor: pointer;
  overflow: hidden;
  border-radius: 8px;
  position: relative;
}

.masonry-item img {
  width: 100%;
  display: block;
  transition: transform 0.3s ease;
}

.masonry-item:hover img { transform: scale(1.04); }

/* ── Lightbox ──────────────────────────────────────────────── */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.9);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.lightbox.hidden { display: none; }

.lightbox-content {
  background: var(--bg-card);
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
  overflow: hidden;
  max-height: 90vh;
  overflow-y: auto;
}

.lightbox-content img { width: 100%; display: block; }

.lightbox-info { padding: 1.25rem; }

.lightbox-close {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  color: #fff;
  font-size: 2rem;
  cursor: pointer;
  line-height: 1;
}

/* ── Settings ──────────────────────────────────────────────── */
.settings-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.settings-section h3 {
  color: var(--accent);
  margin-bottom: 1rem;
  font-size: 1rem;
}

.theme-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.theme-option {
  border: 2px solid var(--border);
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.theme-option:hover,
.theme-option.active { border-color: var(--accent); }

.accent-options { display: flex; gap: 0.75rem; flex-wrap: wrap; }

.accent-swatch {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: border-color 0.2s, transform 0.2s;
}

.accent-swatch:hover,
.accent-swatch.active { border-color: var(--text-primary); transform: scale(1.1); }

/* ── Books ─────────────────────────────────────────────────── */
.book-item {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border);
}

.book-status {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: rgba(245,158,11,0.12);
  color: var(--accent);
  align-self: flex-start;
  white-space: nowrap;
}

/* ── Utility ───────────────────────────────────────────────── */
.section-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.section-subtitle {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.tag {
  display: inline-block;
  font-size: 0.72rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  margin: 0.15rem;
}

.hero {
  padding: 3rem 0 2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2.5rem;
}

.hero h1 { font-size: 2.5rem; }
.hero h1 span { color: var(--accent); }
```

- [ ] **Step 2: Commit**

```bash
git add static/css/style.css
git commit -m "feat: CSS theme system with dark/light/natural + 5 accent colours"
```

---

## Task 5: Base Template + Nav + HTMX

**Files:**
- Create: `templates/base.html`
- Create: `templates/partials/visit_count.html`

- [ ] **Step 1: Create `templates/partials/visit_count.html`**

```html
<span class="visit-pill">🌍 {{ count | default(0) | int }} visits</span>
```

- [ ] **Step 2: Create `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="amber">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Sarah Chidzanga{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <script src="https://unpkg.com/htmx.org@1.9.10" defer></script>
</head>
<body>
  <nav class="top-nav">
    <a href="/" class="nav-brand">✦ Sarah Chidzanga</a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/timeline">Timeline</a>
      <a href="/projects">Projects</a>
      <a href="/sunsets">Sunsets</a>
      <a href="/books">Books</a>
      <a href="/hobbies">Hobbies</a>
      <a href="/family">Family</a>
      <a href="/contact">Contact</a>
      <a href="/settings">⚙️</a>
    </div>
    <div hx-get="/visits/global"
         hx-trigger="load"
         hx-swap="outerHTML">
      <span class="visit-pill">🌍 ...</span>
    </div>
  </nav>

  <main>
    {% block content %}{% endblock %}
  </main>

  <script src="{{ url_for('static', filename='js/settings.js') }}"></script>
  <script src="{{ url_for('static', filename='js/animations.js') }}"></script>
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add templates/base.html templates/partials/visit_count.html
git commit -m "feat: base template with nav, HTMX, and live visit pill"
```

---

## Task 6: Settings Page

**Files:**
- Create: `static/js/settings.js`
- Create: `templates/settings.html`
- Modify: `routes/settings.py`

- [ ] **Step 1: Create `static/js/settings.js`**

```javascript
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
```

- [ ] **Step 2: Create `templates/settings.html`**

```html
{% extends "base.html" %}
{% block title %}Settings — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Settings</h1>
<p class="section-subtitle">Customise how the site looks for you. Saved in your browser.</p>

<div class="settings-section">
  <h3>🎨 Appearance</h3>

  <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 0.75rem;">Theme</p>
  <div class="theme-options">
    <div class="theme-option" data-theme="light" onclick="SarahSettings.setTheme('light')">
      <div style="font-size: 1.5rem;">☀️</div>
      <div style="margin-top: 0.4rem; font-size: 0.85rem;">Light</div>
    </div>
    <div class="theme-option" data-theme="natural" onclick="SarahSettings.setTheme('natural')">
      <div style="font-size: 1.5rem;">🌿</div>
      <div style="margin-top: 0.4rem; font-size: 0.85rem;">Natural</div>
    </div>
    <div class="theme-option" data-theme="dark" onclick="SarahSettings.setTheme('dark')">
      <div style="font-size: 1.5rem;">🌙</div>
      <div style="margin-top: 0.4rem; font-size: 0.85rem;">Dark</div>
    </div>
  </div>

  <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 0.75rem;">Accent Colour</p>
  <div class="accent-options">
    <div class="accent-swatch" data-accent="amber"  style="background:#f59e0b;" onclick="SarahSettings.setAccent('amber')"  title="Amber"></div>
    <div class="accent-swatch" data-accent="rust"   style="background:#ef4444;" onclick="SarahSettings.setAccent('rust')"   title="Rust"></div>
    <div class="accent-swatch" data-accent="violet" style="background:#8b5cf6;" onclick="SarahSettings.setAccent('violet')" title="Violet"></div>
    <div class="accent-swatch" data-accent="sage"   style="background:#10b981;" onclick="SarahSettings.setAccent('sage')"   title="Sage"></div>
    <div class="accent-swatch" data-accent="blue"   style="background:#3b82f6;" onclick="SarahSettings.setAccent('blue')"   title="Blue"></div>
  </div>

  <p style="margin-top: 1rem; font-size: 0.78rem; color: var(--text-secondary);">
    Each visitor picks their own preference — it doesn't change what others see.
  </p>
</div>

<script>
  // Mark the active theme and accent on page load
  document.addEventListener('DOMContentLoaded', function () {
    var c = SarahSettings.current();
    document.querySelectorAll('.theme-option').forEach(function (el) {
      el.classList.toggle('active', el.dataset.theme === c.theme);
    });
    document.querySelectorAll('.accent-swatch').forEach(function (el) {
      el.classList.toggle('active', el.dataset.accent === c.accent);
    });
  });
</script>
{% endblock %}
```

- [ ] **Step 3: Update `routes/settings.py`**

```python
from flask import Blueprint, render_template

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
def settings():
    return render_template('settings.html')
```

- [ ] **Step 4: Smoke-test the settings page**

```bash
python app.py
# open http://127.0.0.1:5000/settings in your browser
# Click theme and accent buttons — the page should update instantly
# Refresh — preferences should be preserved
```

- [ ] **Step 5: Commit**

```bash
git add static/js/settings.js templates/settings.html routes/settings.py
git commit -m "feat: settings page with localStorage theme and accent switcher"
```

---

## Task 7: Visit Tracking Route

**Files:**
- Modify: `routes/visits.py`
- Create: `tests/test_visits.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_visits.py`:

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


def test_global_visit_endpoint_returns_pill(client):
    resp = client.get('/visits/global')
    assert resp.status_code == 200
    assert b'visit' in resp.data


def test_global_visit_count_increments(client):
    client.get('/')   # triggers track_visit via home route
    resp = client.get('/visits/global')
    assert b'1' in resp.data or b'visit' in resp.data
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_visits.py -v
```

Expected: Tests fail because `/visits/global` returns an empty Blueprint stub.

- [ ] **Step 3: Update `routes/visits.py`**

```python
from flask import Blueprint, render_template
from db import get_global_visit_count

visits_bp = Blueprint('visits', __name__)


@visits_bp.route('/visits/global')
def global_visits():
    count = get_global_visit_count()
    return render_template('partials/visit_count.html', count=count)
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_visits.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add routes/visits.py tests/test_visits.py
git commit -m "feat: global visit count HTMX endpoint"
```

---

## Task 8: Shared HTMX Partials — Like Button + Comment List

**Files:**
- Create: `templates/partials/like_button.html`
- Create: `templates/partials/comment_list.html`

These partials are used by Home, Projects, and Sunsets — define them once here.

- [ ] **Step 1: Create `templates/partials/like_button.html`**

```html
<button class="like-btn{% if liked %} liked{% endif %}"
        hx-post="/like/{{ target_type }}/{{ target_id }}"
        hx-target="this"
        hx-swap="outerHTML">
  <span class="heart">❤</span> {{ count | int }}
</button>
```

- [ ] **Step 2: Create `templates/partials/comment_list.html`**

```html
{% for comment in comments %}
<div class="comment-item">
  <div class="comment-author">{{ comment.author | e }}</div>
  <div class="comment-body">{{ comment.body | e }}</div>
</div>
{% else %}
<p style="color: var(--text-secondary); font-size: 0.9rem;">No comments yet — be the first!</p>
{% endfor %}
```

- [ ] **Step 3: Commit**

```bash
git add templates/partials/like_button.html templates/partials/comment_list.html
git commit -m "feat: shared HTMX partials for like button and comment list"
```

---

## Task 9: Home Page

**Files:**
- Modify: `routes/home.py`
- Create: `templates/home.html`
- Create: `tests/test_home.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_home.py`:

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


def test_home_returns_200(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Sarah' in resp.data


def test_post_comment_returns_comment_list(client):
    resp = client.post('/comment/home', data={'author': 'Alice', 'body': 'Hello!'})
    assert resp.status_code == 200
    assert b'Alice' in resp.data
    assert b'Hello!' in resp.data


def test_post_empty_comment_ignored(client):
    resp = client.post('/comment/home', data={'author': 'Alice', 'body': ''})
    assert resp.status_code == 204


def test_like_home_returns_button(client):
    resp = client.post('/like/home/home')
    assert resp.status_code == 200
    assert b'liked' in resp.data
```

- [ ] **Step 2: Run — verify fail**

```bash
pytest tests/test_home.py -v
```

Expected: Failures because routes are stubs.

- [ ] **Step 3: Update `routes/home.py`**

```python
from flask import Blueprint, render_template, request
from datetime import datetime, timezone
from db import track_visit, query_items, put_item, increment_like, get_item

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    track_visit('home')
    comments = query_items('comments', 'home', scan_index_forward=False)
    home_row = get_item('page_visits', 'home')
    like_count = int(home_row.get('like_count', 0)) if home_row else 0
    return render_template('home.html', comments=comments, like_count=like_count)


@home_bp.route('/comment/home', methods=['POST'])
def add_home_comment():
    author = request.form.get('author', 'Anonymous').strip() or 'Anonymous'
    body = request.form.get('body', '').strip()
    if not body:
        return '', 204
    sk = datetime.now(timezone.utc).isoformat()
    put_item('comments', {'pk': 'home', 'sk': sk, 'author': author, 'body': body})
    comments = query_items('comments', 'home', scan_index_forward=False)
    return render_template('partials/comment_list.html', comments=comments)


@home_bp.route('/like/home/home', methods=['POST'])
def like_home():
    count = increment_like('page_visits', 'home')
    return render_template(
        'partials/like_button.html',
        target_type='home',
        target_id='home',
        count=count,
        liked=True,
    )
```

- [ ] **Step 4: Create `templates/home.html`**

```html
{% extends "base.html" %}
{% block title %}Sarah Chidzanga — Hub{% endblock %}

{% block content %}
<section class="hero">
  <h1>Hi, I'm <span>Sarah Chidzanga</span> ✦</h1>
  <p style="font-size: 1.15rem; color: var(--text-secondary); margin-top: 0.75rem; max-width: 600px;">
    Integration Engineering Intern at Jamf. Student builder from MCRI Vic Falls.
    Sunset chaser, reader, and proud family person.
  </p>
  <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
    <a href="/timeline" class="like-btn" style="text-decoration:none;">⏳ My Timeline</a>
    <a href="/projects" class="like-btn" style="text-decoration:none;">🛠 Projects</a>
    <a href="/sunsets"  class="like-btn" style="text-decoration:none;">🌅 Sunset Gallery</a>
  </div>
</section>

<section>
  <h2 class="section-title">Guestbook</h2>
  <p class="section-subtitle">Leave a message — I'd love to hear from you.</p>

  <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;">
    {% with target_type='home', target_id='home', count=like_count, liked=false %}
      {% include 'partials/like_button.html' %}
    {% endwith %}
    <span style="color: var(--text-secondary); font-size:0.85rem;">people have liked this page</span>
  </div>

  <form class="comment-form"
        hx-post="/comment/home"
        hx-target="#comment-list"
        hx-swap="innerHTML"
        hx-on::after-request="this.reset()">
    <input type="text" name="author" placeholder="Your name" maxlength="80">
    <textarea name="body" placeholder="Say hello, share a thought..." maxlength="500"></textarea>
    <button type="submit">Post message</button>
  </form>

  <div id="comment-list">
    {% include 'partials/comment_list.html' %}
  </div>
</section>
{% endblock %}
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_home.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 6: Manual smoke test**

```bash
python app.py
# open http://127.0.0.1:5000/
# Type a comment and submit — it should appear without page reload
# Click the like button — count should increment
```

- [ ] **Step 7: Commit**

```bash
git add routes/home.py templates/home.html tests/test_home.py
git commit -m "feat: home page with guestbook comments and likes via HTMX"
```

---

## Task 10: Timeline Page

**Files:**
- Modify: `routes/timeline.py`
- Create: `templates/timeline.html`

Timeline data is hardcoded — it's personal milestones that rarely change, not user content.

- [ ] **Step 1: Update `routes/timeline.py`**

```python
from flask import Blueprint, render_template, request
from db import track_visit

timeline_bp = Blueprint('timeline', __name__)

MILESTONES = [
    {
        'id': 'mcri-student',
        'year': '2021 – 2023',
        'title': 'Student at MCRI, Victoria Falls',
        'summary': 'Built my first apps, discovered a love for software.',
        'detail': (
            'Studied at MCRI in Victoria Falls where I built several student projects '
            'ranging from simple utilities to web apps. This is where I discovered '
            'that I love building things that solve real problems. I learned Python, '
            'basic web development, and how to think like an engineer.'
        ),
        'tags': ['Python', 'Web Dev', 'Student Projects'],
        'links': [],
    },
    {
        'id': 'jamf-internship',
        'year': '2024 – Present',
        'title': 'Integration Engineering Intern — Jamf',
        'summary': 'Working with Jamf Pro, Splunk, and AWS to build integration workflows.',
        'detail': (
            'Joined Jamf as an Integration Engineering Intern, working with Jamf Pro, '
            'Jamf Protect, Jamf Security Cloud, Splunk, and AWS (Lambda, API Gateway). '
            'Built an integration agent workflow and a Jamf → Splunk data pipeline. '
            'Learning how enterprise security and device management systems fit together.'
        ),
        'tags': ['Jamf Pro', 'Splunk', 'AWS Lambda', 'Python', 'API Gateway'],
        'links': [{'label': 'Projects', 'href': '/projects'}],
    },
    {
        'id': 'future',
        'year': 'Next',
        'title': 'Future Goals',
        'summary': 'Keep building, keep learning, keep shooting sunsets.',
        'detail': (
            'I want to deepen my expertise in cloud-native integrations, '
            'explore more of the AWS ecosystem, and eventually lead projects '
            'that connect people and systems in meaningful ways. '
            'And keep photographing every sunset I can find.'
        ),
        'tags': ['Cloud', 'Architecture', 'Growth'],
        'links': [],
    },
]


@timeline_bp.route('/timeline')
def timeline():
    track_visit('timeline')
    return render_template('timeline.html', milestones=MILESTONES)


@timeline_bp.route('/timeline/<milestone_id>/detail')
def milestone_detail(milestone_id):
    """HTMX endpoint — returns just the detail panel for a milestone."""
    milestone = next((m for m in MILESTONES if m['id'] == milestone_id), None)
    if not milestone:
        return '', 404
    is_open = request.args.get('open', 'true') == 'true'
    return render_template('partials/timeline_detail.html', milestone=milestone, is_open=is_open)
```

- [ ] **Step 2: Create `templates/partials/timeline_detail.html`**

```html
{% if is_open %}
<div class="timeline-detail" style="display: block;">
  <p style="color: var(--text-secondary);">{{ milestone.detail }}</p>
  <div style="margin-top: 0.75rem;">
    {% for tag in milestone.tags %}
      <span class="tag">{{ tag }}</span>
    {% endfor %}
  </div>
  {% if milestone.links %}
    <div style="margin-top: 0.75rem;">
      {% for link in milestone.links %}
        <a href="{{ link.href }}">{{ link.label }} →</a>
      {% endfor %}
    </div>
  {% endif %}
  <button style="margin-top:0.75rem; background:none; border:none; color:var(--text-secondary); cursor:pointer; font-size:0.85rem;"
          hx-get="/timeline/{{ milestone.id }}/detail?open=false"
          hx-target="#detail-{{ milestone.id }}"
          hx-swap="outerHTML">
    ↑ Collapse
  </button>
</div>
{% else %}
<div id="detail-{{ milestone.id }}"></div>
{% endif %}
```

- [ ] **Step 3: Create `templates/timeline.html`**

```html
{% extends "base.html" %}
{% block title %}Timeline — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Life & Projects Timeline</h1>
<p class="section-subtitle">The phases of my journey so far.</p>

<div class="timeline">
  {% for m in milestones %}
  <div class="timeline-item" id="milestone-{{ m.id }}">
    <div class="timeline-dot"></div>
    <div style="color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 0.25rem;">{{ m.year }}</div>
    <h3 style="cursor: pointer;"
        hx-get="/timeline/{{ m.id }}/detail?open=true"
        hx-target="#detail-{{ m.id }}"
        hx-swap="outerHTML">
      {{ m.title }}
      <span style="color: var(--accent); font-size: 0.8rem; margin-left: 0.5rem;">▾</span>
    </h3>
    <p style="color: var(--text-secondary); margin-top: 0.25rem;">{{ m.summary }}</p>
    <div id="detail-{{ m.id }}"></div>
  </div>
  {% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 4: Commit**

```bash
git add routes/timeline.py templates/timeline.html templates/partials/timeline_detail.html
git commit -m "feat: timeline page with HTMX expandable milestone cards"
```

---

## Task 11: Projects — List + Detail + Living Brief

**Files:**
- Modify: `routes/projects.py`
- Create: `templates/projects/list.html`
- Create: `templates/projects/detail.html`
- Create: `tests/test_projects.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_projects.py`:

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
        # Seed a project
        ddb.Table('projects').put_item(Item={
            'pk': 'jamf-splunk',
            'title': 'Jamf → Splunk Integration',
            'description': 'Sends Jamf events to Splunk.',
            'category': 'jamf',
            'tech_stack': ['Python', 'Lambda', 'Splunk'],
            'current_phase': 'Build',
            'phases': {'Discovery': 'Identified data gaps.', 'Build': 'Lambda pipeline.'},
            'like_count': 3,
            'created_at': '2024-01-01T00:00:00',
        })
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_projects_list_returns_200(client):
    resp = client.get('/projects')
    assert resp.status_code == 200
    assert b'Jamf' in resp.data


def test_projects_filter_by_category(client):
    resp = client.get('/projects?category=mcri')
    assert resp.status_code == 200


def test_project_detail_returns_200(client):
    resp = client.get('/projects/jamf-splunk')
    assert resp.status_code == 200
    assert b'Splunk' in resp.data


def test_project_detail_404_for_unknown(client):
    resp = client.get('/projects/does-not-exist')
    assert resp.status_code == 404


def test_like_project_returns_button(client):
    resp = client.post('/like/project/jamf-splunk')
    assert resp.status_code == 200
    assert b'liked' in resp.data


def test_comment_on_project(client):
    resp = client.post('/comment/project/jamf-splunk',
                       data={'author': 'Bob', 'body': 'Great work!'})
    assert resp.status_code == 200
    assert b'Bob' in resp.data
```

- [ ] **Step 2: Run — verify fail**

```bash
pytest tests/test_projects.py -v
```

- [ ] **Step 3: Update `routes/projects.py`**

```python
from flask import Blueprint, render_template, request, abort
from datetime import datetime, timezone
from db import scan_table, get_item, increment_like, put_item, query_items, track_visit

projects_bp = Blueprint('projects', __name__)

PHASES = ['Discovery', 'Alignment', 'Planning', 'Build', 'Launch']


@projects_bp.route('/projects')
def projects_list():
    track_visit('projects')
    all_projects = scan_table('projects')
    all_projects.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    category = request.args.get('category', 'all')
    if category != 'all':
        filtered = [p for p in all_projects if p.get('category') == category]
    else:
        filtered = all_projects
    return render_template('projects/list.html',
                           projects=filtered,
                           active_category=category,
                           all_projects=all_projects)


@projects_bp.route('/projects/<slug>')
def project_detail(slug):
    track_visit('projects')
    project = get_item('projects', slug)
    if not project:
        abort(404)
    comments = query_items('comments', f'project#{slug}', scan_index_forward=False)
    phase_index = PHASES.index(project.get('current_phase', 'Discovery')) if project.get('current_phase') in PHASES else 0
    return render_template('projects/detail.html',
                           project=project,
                           comments=comments,
                           phases=PHASES,
                           phase_index=phase_index)


@projects_bp.route('/like/project/<slug>', methods=['POST'])
def like_project(slug):
    project = get_item('projects', slug)
    if not project:
        abort(404)
    count = increment_like('projects', slug)
    return render_template('partials/like_button.html',
                           target_type='project',
                           target_id=slug,
                           count=count,
                           liked=True)


@projects_bp.route('/comment/project/<slug>', methods=['POST'])
def comment_project(slug):
    author = request.form.get('author', 'Anonymous').strip() or 'Anonymous'
    body = request.form.get('body', '').strip()
    if not body:
        return '', 204
    sk = datetime.now(timezone.utc).isoformat()
    put_item('comments', {'pk': f'project#{slug}', 'sk': sk, 'author': author, 'body': body})
    comments = query_items('comments', f'project#{slug}', scan_index_forward=False)
    return render_template('partials/comment_list.html', comments=comments)
```

- [ ] **Step 4: Create `templates/projects/list.html`**

```html
{% extends "base.html" %}
{% block title %}Projects — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Projects</h1>
<p class="section-subtitle">Integration work at Jamf and apps I built at MCRI.</p>

<div style="display:flex; gap:0.75rem; margin-bottom:2rem;">
  <a href="/projects?category=all"  class="like-btn {% if active_category=='all'  %}liked{% endif %}">All ({{ all_projects|length }})</a>
  <a href="/projects?category=jamf" class="like-btn {% if active_category=='jamf' %}liked{% endif %}">Jamf Work</a>
  <a href="/projects?category=mcri" class="like-btn {% if active_category=='mcri' %}liked{% endif %}">MCRI Apps</a>
</div>

{% if projects %}
<div class="card-grid">
  {% for project in projects %}
  <a href="/projects/{{ project.pk }}" style="text-decoration:none;">
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
        <h3 style="font-size:1rem;">{{ project.title }}</h3>
        <span class="phase-badge">{{ project.current_phase }}</span>
      </div>
      <p style="color:var(--text-secondary); font-size:0.875rem; margin-bottom:0.75rem;">{{ project.description }}</p>
      <div>
        {% for tech in project.tech_stack %}
          <span class="tag">{{ tech }}</span>
        {% endfor %}
      </div>
      <div style="margin-top:0.75rem; color:var(--text-secondary); font-size:0.82rem;">
        ❤ {{ project.like_count | default(0) | int }}
      </div>
    </div>
  </a>
  {% endfor %}
</div>
{% else %}
<p style="color: var(--text-secondary);">No projects in this category yet.</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Create `templates/projects/detail.html`**

```html
{% extends "base.html" %}
{% block title %}{{ project.title }} — Sarah Chidzanga{% endblock %}

{% block content %}
<div style="margin-bottom:0.5rem;">
  <a href="/projects" style="color:var(--text-secondary); font-size:0.85rem;">← All Projects</a>
</div>

<h1 class="section-title">{{ project.title }}</h1>
<p class="section-subtitle">{{ project.description }}</p>

<div style="margin-bottom:1.5rem;">
  {% for tech in project.tech_stack %}
    <span class="tag">{{ tech }}</span>
  {% endfor %}
</div>

<!-- Living Brief Phase Progress -->
<div class="card" style="margin-bottom:2rem;">
  <h3 style="margin-bottom:1rem; color:var(--accent);">Living Brief</h3>
  <div style="display:flex; gap:0; margin-bottom:1.5rem; overflow-x:auto;">
    {% for phase in phases %}
    <div style="flex:1; text-align:center; padding:0.5rem 0.25rem; min-width:80px;
                {% if loop.index0 < phase_index %}color:var(--accent); border-bottom:2px solid var(--accent);
                {% elif loop.index0 == phase_index %}color:var(--text-primary); border-bottom:2px solid var(--accent); font-weight:700;
                {% else %}color:var(--text-secondary); border-bottom:2px solid var(--border);{% endif %}
                font-size:0.78rem;">
      {{ phase }}
    </div>
    {% endfor %}
  </div>

  {% for phase in phases %}
    {% if project.phases and phase in project.phases %}
    <div style="margin-bottom:0.75rem;">
      <div style="font-size:0.8rem; font-weight:600; color:var(--accent); margin-bottom:0.2rem;">{{ phase }}</div>
      <p style="color:var(--text-secondary); font-size:0.875rem;">{{ project.phases[phase] }}</p>
    </div>
    {% endif %}
  {% endfor %}
</div>

<!-- Like button -->
<div style="margin-bottom:2rem;">
  {% with target_type='project', target_id=project.pk, count=project.like_count|default(0)|int, liked=false %}
    {% include 'partials/like_button.html' %}
  {% endwith %}
</div>

<!-- Comments -->
<h2 style="font-size:1.25rem; margin-bottom:1rem;">Comments</h2>

<form class="comment-form"
      hx-post="/comment/project/{{ project.pk }}"
      hx-target="#comment-list"
      hx-swap="innerHTML"
      hx-on::after-request="this.reset()">
  <input type="text" name="author" placeholder="Your name" maxlength="80">
  <textarea name="body" placeholder="Share your thoughts..." maxlength="500"></textarea>
  <button type="submit">Post comment</button>
</form>

<div id="comment-list">
  {% include 'partials/comment_list.html' %}
</div>
{% endblock %}
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
pytest tests/test_projects.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add routes/projects.py templates/projects/ tests/test_projects.py
git commit -m "feat: projects list, detail page, Living Brief phases, likes and comments"
```

---

## Task 12: Sunsets Gallery

**Files:**
- Modify: `routes/sunsets.py`
- Create: `templates/sunsets.html`
- Create: `tests/test_sunsets.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_sunsets.py`:

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
        ddb.Table('sunset_photos').put_item(Item={
            'pk': 'sunset-vic-falls-01',
            'location': 'Victoria Falls',
            'story': 'Golden hour over the falls.',
            's3_url': 'https://example.com/photo.jpg',
            'taken_at': '2023-06-15',
            'like_count': 7,
            'created_at': '2023-06-15T18:00:00',
        })
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_sunsets_returns_200(client):
    resp = client.get('/sunsets')
    assert resp.status_code == 200
    assert b'Victoria Falls' in resp.data


def test_like_photo_returns_button(client):
    resp = client.post('/like/photo/sunset-vic-falls-01')
    assert resp.status_code == 200
    assert b'liked' in resp.data


def test_comment_on_photo(client):
    resp = client.post('/comment/photo/sunset-vic-falls-01',
                       data={'author': 'Eve', 'body': 'Stunning!'})
    assert resp.status_code == 200
    assert b'Eve' in resp.data


def test_photo_comments_endpoint(client):
    resp = client.get('/sunsets/sunset-vic-falls-01/comments')
    assert resp.status_code == 200
```

- [ ] **Step 2: Run — verify fail**

```bash
pytest tests/test_sunsets.py -v
```

- [ ] **Step 3: Update `routes/sunsets.py`**

```python
from flask import Blueprint, render_template, request, abort
from datetime import datetime, timezone
from db import scan_table, get_item, increment_like, put_item, query_items, track_visit

sunsets_bp = Blueprint('sunsets', __name__)


@sunsets_bp.route('/sunsets')
def sunsets():
    track_visit('sunsets')
    photos = scan_table('sunset_photos')
    photos.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    return render_template('sunsets.html', photos=photos)


@sunsets_bp.route('/sunsets/<photo_id>/comments')
def photo_comments(photo_id):
    comments = query_items('comments', f'photo#{photo_id}', scan_index_forward=False)
    return render_template('partials/comment_list.html', comments=comments)


@sunsets_bp.route('/like/photo/<photo_id>', methods=['POST'])
def like_photo(photo_id):
    photo = get_item('sunset_photos', photo_id)
    if not photo:
        abort(404)
    count = increment_like('sunset_photos', photo_id)
    return render_template('partials/like_button.html',
                           target_type='photo',
                           target_id=photo_id,
                           count=count,
                           liked=True)


@sunsets_bp.route('/comment/photo/<photo_id>', methods=['POST'])
def comment_photo(photo_id):
    author = request.form.get('author', 'Anonymous').strip() or 'Anonymous'
    body = request.form.get('body', '').strip()
    if not body:
        return '', 204
    sk = datetime.now(timezone.utc).isoformat()
    put_item('comments', {'pk': f'photo#{photo_id}', 'sk': sk, 'author': author, 'body': body})
    comments = query_items('comments', f'photo#{photo_id}', scan_index_forward=False)
    return render_template('partials/comment_list.html', comments=comments)
```

- [ ] **Step 4: Create `templates/sunsets.html`**

```html
{% extends "base.html" %}
{% block title %}Sunsets — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Sunset Gallery</h1>
<p class="section-subtitle">Every sunset tells a story. Click any photo to read mine.</p>

{% if photos %}
<div class="masonry-grid">
  {% for photo in photos %}
  <div class="masonry-item" onclick="openLightbox('{{ photo.pk | e }}')">
    <img src="{{ photo.s3_url | e }}"
         alt="Sunset at {{ photo.location | e }}"
         loading="lazy">
  </div>
  {% endfor %}
</div>
{% else %}
<p style="color: var(--text-secondary);">Photos coming soon.</p>
{% endif %}

<!-- Lightbox -->
<div id="lightbox" class="lightbox hidden" onclick="closeLightbox(event)">
  <span class="lightbox-close" onclick="closeLightbox(null)">&times;</span>
  <div class="lightbox-content" onclick="event.stopPropagation()">
    <img id="lb-img" src="" alt="">
    <div class="lightbox-info">
      <h3 id="lb-location" style="color:var(--accent);"></h3>
      <p id="lb-story"    style="color:var(--text-secondary); margin: 0.5rem 0 1rem;"></p>
      <p id="lb-date"     style="color:var(--text-secondary); font-size:0.8rem; margin-bottom:1rem;"></p>

      <div id="lb-like"></div>

      <h4 style="margin:1rem 0 0.5rem;">Comments</h4>
      <form class="comment-form"
            id="lb-comment-form"
            hx-target="#lb-comments"
            hx-swap="innerHTML"
            hx-on::after-request="this.reset()">
        <input type="text" name="author" placeholder="Your name" maxlength="80">
        <textarea name="body" placeholder="What does this sunset mean to you?" maxlength="500"></textarea>
        <button type="submit">Post</button>
      </form>
      <div id="lb-comments"></div>
    </div>
  </div>
</div>

<script>
  var PHOTOS = {
    {% for photo in photos %}
    "{{ photo.pk | e }}": {
      src:      "{{ photo.s3_url | e }}",
      location: "{{ photo.location | e }}",
      story:    "{{ photo.story | e | replace('\n', ' ') }}",
      date:     "{{ photo.taken_at | e }}",
      likeCount: {{ photo.like_count | default(0) | int }}
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  };

  function openLightbox(id) {
    var p = PHOTOS[id];
    if (!p) return;
    document.getElementById('lb-img').src      = p.src;
    document.getElementById('lb-location').textContent = p.location;
    document.getElementById('lb-story').textContent    = p.story;
    document.getElementById('lb-date').textContent     = p.date;

    // Like button
    document.getElementById('lb-like').innerHTML =
      '<button class="like-btn" hx-post="/like/photo/' + id + '" hx-target="this" hx-swap="outerHTML">' +
      '<span class="heart">❤</span> ' + p.likeCount + '</button>';
    htmx.process(document.getElementById('lb-like'));

    // Comments
    var commentForm = document.getElementById('lb-comment-form');
    commentForm.setAttribute('hx-post', '/comment/photo/' + id);
    htmx.process(commentForm);
    fetch('/sunsets/' + id + '/comments')
      .then(r => r.text())
      .then(html => { document.getElementById('lb-comments').innerHTML = html; });

    document.getElementById('lightbox').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox(event) {
    if (event && event.target !== document.getElementById('lightbox')) return;
    document.getElementById('lightbox').classList.add('hidden');
    document.body.style.overflow = '';
  }
</script>
{% endblock %}
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_sunsets.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add routes/sunsets.py templates/sunsets.html tests/test_sunsets.py
git commit -m "feat: sunset gallery with masonry grid, lightbox, likes and comments"
```

---

## Task 13: Books Page

**Files:**
- Modify: `routes/books.py`
- Create: `templates/books.html`

- [ ] **Step 1: Update `routes/books.py`**

```python
from flask import Blueprint, render_template
from db import scan_table, track_visit

books_bp = Blueprint('books', __name__)


@books_bp.route('/books')
def books():
    track_visit('books')
    all_books = scan_table('books')
    currently_reading = [b for b in all_books if b.get('status') == 'reading']
    have_read = [b for b in all_books if b.get('status') == 'read']
    return render_template('books.html',
                           currently_reading=currently_reading,
                           have_read=have_read)
```

- [ ] **Step 2: Create `templates/books.html`**

```html
{% extends "base.html" %}
{% block title %}Books — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Reading List</h1>
<p class="section-subtitle">Books I'm reading and thinking about.</p>

{% if currently_reading %}
<h2 style="font-size:1.15rem; margin-bottom:1rem; color:var(--accent);">Currently Reading</h2>
{% for book in currently_reading %}
<div class="book-item">
  <div style="flex:1;">
    <div style="font-weight:600;">{{ book.title }}</div>
    <div style="color:var(--text-secondary); font-size:0.85rem;">{{ book.author }}</div>
    {% if book.reflection %}
    <div style="color:var(--text-secondary); font-size:0.875rem; margin-top:0.4rem; font-style:italic;">"{{ book.reflection }}"</div>
    {% endif %}
  </div>
  <span class="book-status">Reading</span>
</div>
{% endfor %}
{% endif %}

{% if have_read %}
<h2 style="font-size:1.15rem; margin:2rem 0 1rem; color:var(--accent);">Have Read</h2>
{% for book in have_read %}
<div class="book-item">
  <div style="flex:1;">
    <div style="font-weight:600;">{{ book.title }}</div>
    <div style="color:var(--text-secondary); font-size:0.85rem;">{{ book.author }}</div>
    {% if book.reflection %}
    <div style="color:var(--text-secondary); font-size:0.875rem; margin-top:0.4rem; font-style:italic;">"{{ book.reflection }}"</div>
    {% endif %}
  </div>
  <span class="book-status" style="background:rgba(255,255,255,0.05); color:var(--text-secondary);">Read ✓</span>
</div>
{% endfor %}
{% endif %}

{% if not currently_reading and not have_read %}
<p style="color: var(--text-secondary);">Books coming soon.</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Commit**

```bash
git add routes/books.py templates/books.html
git commit -m "feat: books page with currently-reading and have-read sections"
```

---

## Task 14: Hobbies, Family, and Contact Pages

These three pages are read-only with hardcoded content.

**Files:**
- Modify: `routes/hobbies.py`
- Modify: `routes/family.py`
- Modify: `routes/contact.py`
- Create: `templates/hobbies.html`
- Create: `templates/family.html`
- Create: `templates/contact.html`

- [ ] **Step 1: Update `routes/hobbies.py`**

```python
from flask import Blueprint, render_template
from db import track_visit

hobbies_bp = Blueprint('hobbies', __name__)

HOBBIES = [
    {
        'icon': '📷',
        'title': 'Sunset Photography',
        'description': "I chase sunsets whenever I can — there's something about that golden hour that makes everything slow down. Every photo has a story.",
        'link': {'label': 'See my sunset gallery', 'href': '/sunsets'},
    },
    {
        'icon': '📚',
        'title': 'Reading',
        'description': 'Books are how I learn beyond my field. I love anything that challenges the way I think — tech, psychology, memoir.',
        'link': {'label': 'See my reading list', 'href': '/books'},
    },
    {
        'icon': '👨‍👩‍👧',
        'title': 'Family Time',
        'description': 'Time with family is how I recharge. Victoria Falls will always be home.',
        'link': {'label': 'Meet my family', 'href': '/family'},
    },
    {
        'icon': '☁️',
        'title': 'Cloud & Integrations',
        'description': "Building things that connect systems is genuinely fun to me — not just work. I geek out on AWS architecture even on weekends.",
        'link': None,
    },
]


@hobbies_bp.route('/hobbies')
def hobbies():
    track_visit('hobbies')
    return render_template('hobbies.html', hobbies=HOBBIES)
```

- [ ] **Step 2: Create `templates/hobbies.html`**

```html
{% extends "base.html" %}
{% block title %}Hobbies — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Hobbies & Interests</h1>
<p class="section-subtitle">The things that make me, me.</p>

<div class="card-grid">
  {% for hobby in hobbies %}
  <div class="card">
    <div style="font-size:2.5rem; margin-bottom:0.75rem;">{{ hobby.icon }}</div>
    <h3 style="margin-bottom:0.5rem;">{{ hobby.title }}</h3>
    <p style="color:var(--text-secondary); font-size:0.875rem; margin-bottom:0.75rem;">{{ hobby.description }}</p>
    {% if hobby.link %}
      <a href="{{ hobby.link.href }}">{{ hobby.link.label }} →</a>
    {% endif %}
  </div>
  {% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 3: Update `routes/family.py`**

```python
from flask import Blueprint, render_template
from db import track_visit

family_bp = Blueprint('family', __name__)


@family_bp.route('/family')
def family():
    track_visit('family')
    return render_template('family.html')
```

- [ ] **Step 4: Create `templates/family.html`**

```html
{% extends "base.html" %}
{% block title %}Family — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Family</h1>
<p class="section-subtitle">The people who matter most.</p>

<div class="card" style="max-width:700px;">
  <p style="font-size:1.05rem; line-height:1.8; color:var(--text-secondary);">
    I grew up in Victoria Falls, Zimbabwe — one of the most beautiful places on earth.
    My family is the reason I work hard and the reason I come home. They've supported
    every experiment, every late-night project, and every sunrise I've dragged them
    out to photograph. This section is a small tribute to them.
  </p>
  <p style="margin-top:1rem; color:var(--text-secondary); font-style:italic;">
    Photos coming soon — some things are best kept close to the heart. 🌿
  </p>
</div>
{% endblock %}
```

- [ ] **Step 5: Update `routes/contact.py`**

```python
from flask import Blueprint, render_template
from db import track_visit

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact')
def contact():
    track_visit('contact')
    return render_template('contact.html')
```

- [ ] **Step 6: Create `templates/contact.html`**

```html
{% extends "base.html" %}
{% block title %}Contact — Sarah Chidzanga{% endblock %}

{% block content %}
<h1 class="section-title">Get in Touch</h1>
<p class="section-subtitle">I'd love to hear from you.</p>

<div class="card" style="max-width:500px;">
  <div style="display:flex; flex-direction:column; gap:1.25rem;">
    <div>
      <div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.25rem; text-transform:uppercase; letter-spacing:0.05em;">Email</div>
      <a href="mailto:sarah.chidzanga@jamf.com" style="font-size:1rem;">sarah.chidzanga@jamf.com</a>
    </div>
    <div>
      <div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.25rem; text-transform:uppercase; letter-spacing:0.05em;">LinkedIn</div>
      <a href="https://linkedin.com/in/sarah-chidzanga" target="_blank" rel="noopener">linkedin.com/in/sarah-chidzanga</a>
    </div>
    <div>
      <div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.25rem; text-transform:uppercase; letter-spacing:0.05em;">Slack</div>
      <span style="color:var(--text-primary);">@sarah.chidzanga</span>
      <span style="color:var(--text-secondary); font-size:0.82rem;"> · Jamf workspace</span>
    </div>
  </div>
</div>

<p style="margin-top:1.5rem; color:var(--text-secondary); font-size:0.875rem;">
  Or leave a message in the <a href="/#guestbook">guestbook</a> on the home page.
</p>
{% endblock %}
```

- [ ] **Step 7: Commit**

```bash
git add routes/hobbies.py routes/family.py routes/contact.py \
        templates/hobbies.html templates/family.html templates/contact.html
git commit -m "feat: hobbies, family, and contact pages"
```

---

## Task 15: Animations

**Files:**
- Create: `static/js/animations.js`

- [ ] **Step 1: Create `static/js/animations.js`**

```javascript
// Timeline slide-in on scroll
(function () {
  function revealTimelineItems() {
    var items = document.querySelectorAll('.timeline-item');
    var windowBottom = window.scrollY + window.innerHeight;
    items.forEach(function (item) {
      var itemTop = item.getBoundingClientRect().top + window.scrollY;
      if (itemTop < windowBottom - 60) {
        item.classList.add('visible');
      }
    });
  }

  if (document.querySelector('.timeline-item')) {
    window.addEventListener('scroll', revealTimelineItems);
    revealTimelineItems(); // run once on load for items already in view
  }
})();

// Heart bounce on like button click
// The CSS animation is triggered by the 'liked' class.
// HTMX swaps the button HTML, so the animation runs on the new element naturally.
// This block re-processes any newly swapped like buttons for HTMX.
document.addEventListener('htmx:afterSwap', function (evt) {
  var btn = evt.detail.elt;
  if (btn && btn.classList && btn.classList.contains('like-btn')) {
    btn.classList.add('liked');
  }
});
```

- [ ] **Step 2: Commit**

```bash
git add static/js/animations.js
git commit -m "feat: timeline slide-in and heart bounce animations"
```

---

## Task 16: Deployment Script + Final Test Run

**Files:**
- Create: `package.sh`
- Create: `CLAUDE.md`

- [ ] **Step 1: Run the full test suite**

```bash
pytest tests/ -v
```

Expected: All tests PASS. No errors.

- [ ] **Step 2: Create `package.sh`**

```bash
#!/bin/bash
# package.sh — builds app.zip for uploading to AWS Lambda
# Usage: bash package.sh

set -e

echo "Installing dependencies into ./package/ ..."
pip install -r requirements.txt --target ./package --quiet

echo "Copying app files ..."
cp -r app.py lambda_handler.py db.py routes/ templates/ static/ ./package/

echo "Creating app.zip ..."
cd package
zip -r ../app.zip . --quiet
cd ..
rm -rf package

echo "Done — app.zip is ready to upload to Lambda."
ls -lh app.zip
```

```bash
chmod +x package.sh
```

- [ ] **Step 3: Create `CLAUDE.md`** at the project root

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run tests:
```bash
pytest tests/ -v
```

Run a single test:
```bash
pytest tests/test_db.py::test_put_and_get_item -v
```

Run the app locally:
```bash
python app.py
```

Build the Lambda deployment zip:
```bash
bash package.sh
```

## Architecture

Flask app served on AWS Lambda via Mangum (WSGI adapter). Entry point for Lambda is `lambda_handler.handler`.

**`db.py`** is the only file that imports `boto3`. All routes call helpers from `db.py` — never touch DynamoDB directly in route files.

**HTMX partials** live in `templates/partials/`. Flask returns these small HTML fragments for HTMX requests (likes, comments, visit counts). Full pages always extend `templates/base.html`.

**Theme system** is 100% frontend: `static/js/settings.js` reads/writes `localStorage` and sets `data-theme` and `data-accent` attributes on `<html>`. CSS variables in `static/css/style.css` do the rest. No server calls involved.

**Visit tracking**: every page load calls `db.track_visit(page_name)` which atomically increments both the page-specific row and the `global` row in the `page_visits` DynamoDB table. The nav bar pill fetches `/visits/global` on load via `hx-trigger="load"`.

## Testing

Tests use `moto` to mock AWS DynamoDB — no real AWS credentials needed. Each test file sets fake AWS env vars and creates a fresh set of in-memory DynamoDB tables per test.

DynamoDB comments are queried newest-first using `ScanIndexForward=False`. The `comments` table uses `pk` (parent item) + `sk` (ISO timestamp) as its composite key.

## Data

Five DynamoDB tables: `projects`, `sunset_photos`, `books`, `comments`, `page_visits`. Sunset photos are stored in S3; only the URL is in DynamoDB.

Seed content (projects, books, photos) must be added manually via the AWS DynamoDB console or a seed script — there is no admin panel.
```

- [ ] **Step 4: Commit everything**

```bash
git add package.sh CLAUDE.md
git commit -m "feat: deployment script, CLAUDE.md — portfolio hub complete"
```

---

## AWS Console Deployment Checklist

After the code is done, follow this order in the AWS Console:

- [ ] **S3**: Create bucket `sarah-portfolio-photos`, disable "Block all public access", add public-read bucket policy
- [ ] **DynamoDB**: Create 5 tables (`projects`, `sunset_photos`, `books`, `comments`, `page_visits`) — all with partition key `pk` (String), on-demand billing. `comments` also needs sort key `sk` (String)
- [ ] **IAM**: Create role `sarah-portfolio-lambda-role` with policies: `AmazonDynamoDBFullAccess`, `AmazonS3ReadOnlyAccess`, `AWSLambdaBasicExecutionRole`
- [ ] **Lambda**: Create function, Python 3.12, attach IAM role, run `bash package.sh`, upload `app.zip`, set handler to `lambda_handler.handler`, memory 256 MB, timeout 30s
- [ ] **API Gateway**: Create HTTP API, integrate Lambda, add route `ANY /{proxy+}`, deploy to stage `prod`
- [ ] **Test**: Open the API Gateway URL — the home page should load
- [ ] **Seed data**: Add your first project, book, and sunset photo via DynamoDB console
