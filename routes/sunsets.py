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
