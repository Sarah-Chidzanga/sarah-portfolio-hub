from flask import Blueprint, render_template, request, abort
from datetime import datetime, timezone
from db import scan_table, get_item, increment_like, put_item, query_items, track_visit

projects_bp = Blueprint('projects', __name__)

PHASES = ['Discovery', 'Alignment', 'Planning', 'Build', 'Launch']

_INITIAL_PROJECTS = [
    {
        'pk': 'department-creator',
        'title': 'Department Creator',
        'description': 'Flask app to bulk-create departments in Jamf Pro via the API.',
        'category': 'jamf',
        'tech': 'Flask, AWS Lambda, API Gateway, Jamf Pro API',
        'current_phase': 'Launch',
        'live_url': 'https://a4chajwta6.execute-api.eu-west-1.amazonaws.com',
        'like_count': 0,
    },
    {
        'pk': 'matter-hub',
        'title': 'Matter Hub',
        'description': 'Hackathon project built with my MCRI team — handled documentation, ticket management, and coding.',
        'category': 'mcri',
        'tech': 'Jira, Confluence, Figma, Miro, GitHub',
        'current_phase': 'Launch',
        'github_url': 'https://github.com/iantdzingira/Matter-Hub',
        'like_count': 0,
    },
]


@projects_bp.route('/projects')
def projects_list():
    try:
        track_visit('projects')
    except Exception:
        pass
    try:
        all_projects = scan_table('projects') or []
    except Exception:
        all_projects = []
    # Auto-seed initial projects
    existing_pks = {p['pk'] for p in all_projects}
    for proj in _INITIAL_PROJECTS:
        if proj['pk'] not in existing_pks:
            try:
                put_item('projects', proj)
            except Exception:
                pass
            all_projects.append(proj)
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
