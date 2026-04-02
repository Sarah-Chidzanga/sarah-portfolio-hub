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
