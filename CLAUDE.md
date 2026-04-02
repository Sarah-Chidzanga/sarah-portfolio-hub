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
