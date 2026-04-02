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
