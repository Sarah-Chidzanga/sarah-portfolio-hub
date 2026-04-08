from flask import Blueprint, render_template, request, abort
from datetime import datetime, timezone
from db import scan_table, get_item, increment_like, put_item, query_items, track_visit

sunsets_bp = Blueprint('sunsets', __name__)

_STATIC_SUNSETS = [
    {
        'pk': 'sunset-001',
        's3_url': '/static/images/sunset_001.jpg',
        'location': 'Vic Falls, Kazungula Road',
        'story': (
            'Golden hour through the acacia trees on Kazungula Road. '
            'The light turns everything amber — these are the sunsets I grew up watching.'
        ),
        'taken_at': '2024',
        'like_count': 0,
    },
    {
        'pk': 'sunset-002',
        's3_url': '/static/images/sunset_002.jpg',
        'location': 'Vic Falls, Zimbabwe',
        'story': (
            'A purple and pink sky over Victoria Falls — dramatic clouds '
            'catching the last light of the day.'
        ),
        'taken_at': '2024',
        'like_count': 0,
    },
    {
        'pk': 'sunset-003',
        's3_url': '/static/images/sunset_003.jpg',
        'location': 'Lupane, Zimbabwe',
        'story': (
            'Captured with my water bottle in hand — a memory from Lupane, '
            'where the sun sets quietly behind simple rooftops.'
        ),
        'taken_at': '2024',
        'like_count': 0,
    },
    {
        'pk': 'sunset-004',
        's3_url': '/static/images/sunset_004.jpg',
        'location': 'Monde, Vic Falls',
        'story': (
            'Sunset behind the decorative stone wall in Monde, Victoria Falls. '
            'Globe lights coming on as the orange sky fades to night.'
        ),
        'taken_at': '2024',
        'like_count': 0,
    },
]


@sunsets_bp.route('/sunsets')
def sunsets():
    try:
        track_visit('sunsets')
    except Exception:
        pass
    try:
        photos = scan_table('sunset_photos') or []
    except Exception:
        photos = []
    # Build lookup of static sunsets by pk
    static_by_pk = {s['pk']: s for s in _STATIC_SUNSETS}
    # Keep all photos: use static URLs for static ones, keep others from DynamoDB
    updated_photos = []
    seen_pks = set()
    for photo in photos:
        pk = photo.get('pk')
        if pk in static_by_pk:
            # Use static data to ensure correct local URLs
            updated_photos.append(static_by_pk[pk])
        else:
            # Keep other photos from DynamoDB (old S3 photos)
            updated_photos.append(photo)
        seen_pks.add(pk)
    # Add any missing static sunsets
    for sunset in _STATIC_SUNSETS:
        if sunset['pk'] not in seen_pks:
            try:
                put_item('sunset_photos', sunset)
            except Exception:
                pass
            updated_photos.append(sunset)
    updated_photos.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    return render_template('sunsets.html', photos=updated_photos)


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
