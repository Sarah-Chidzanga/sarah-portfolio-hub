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
