import json
import os
import random
import subprocess
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from db import put_item, query_items

api_bp = Blueprint('api', __name__)

FUN_FACTS = [
    "I grew up in Victoria Falls, Zimbabwe — one of the Seven Natural Wonders of the World.",
    "I chase sunsets with my camera and have never missed a golden hour if I can help it.",
    "I'm an Integration Engineering Intern at Jamf, connecting systems that talk to each other.",
    "I learned to code at MCRI and built my first web app before I turned 20.",
    "I can talk about AWS Lambda architecture for hours and not get tired.",
    "My first Python project was a student timetable app — it actually got used by classmates.",
    "I believe a good integration should be invisible — the less users notice it, the better it works.",
]


def _build_info():
    """Read build_info.json stamped by package.sh, or fall back to git."""
    info_path = os.path.join(os.path.dirname(__file__), '..', 'build_info.json')
    if os.path.exists(info_path):
        with open(info_path) as f:
            return json.load(f)
    # Local dev fallback
    try:
        sha = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        sha = 'unknown'
    return {
        'version': '1.0.0-dev',
        'deploy_timestamp': datetime.now(timezone.utc).isoformat(),
        'commit_sha': sha,
    }


@api_bp.route('/meta')
def meta():
    return jsonify(_build_info())


@api_bp.route('/about')
def about():
    return jsonify({
        'name': 'Sarah Chidzanga',
        'role': 'Integration Engineering Intern',
        'company': 'Jamf',
        'location': 'Victoria Falls, Zimbabwe',
        'bio': (
            'Integration Engineering Intern at Jamf working with Jamf Pro, Jamf Protect, '
            'Jamf Security Cloud, Splunk, and AWS. Former student builder at MCRI, Victoria Falls. '
            'Sunset photographer, reader, and cloud architecture enthusiast.'
        ),
        'skills': [
            'Python', 'Flask', 'AWS Lambda', 'API Gateway', 'DynamoDB',
            'Jamf Pro', 'Splunk', 'GitHub Actions',
        ],
        'currently_learning': ['AWS Solutions Architecture', 'Terraform', 'TypeScript'],
        'links': {
            'portfolio': 'https://sarahchidzanga.com',
            'linkedin': 'https://www.linkedin.com/in/sarah-chidzanga-554028356/',
            'email': 'sarah.chidzanga@jamf.com',
        },
    })


@api_bp.route('/fun-fact')
def fun_fact():
    return jsonify({'fact': random.choice(FUN_FACTS)})


@api_bp.route('/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '') or request.form.get('name', '')).strip()
    email = str(data.get('email', '') or request.form.get('email', '')).strip()
    message = str(data.get('message', '') or request.form.get('message', '')).strip()

    if not name or not email or not message:
        return jsonify({'error': 'name, email, and message are required'}), 400

    sk = datetime.now(timezone.utc).isoformat()
    put_item('comments', {
        'pk': 'contact',
        'sk': sk,
        'author': name,
        'body': f"[{email}] {message}",
    })

    return jsonify({'ok': True, 'message': "Thanks for reaching out — I'll get back to you soon!"}), 201
