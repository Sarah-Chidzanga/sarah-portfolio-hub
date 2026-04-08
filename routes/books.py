from flask import Blueprint, render_template
from db import scan_table, put_item, track_visit

books_bp = Blueprint('books', __name__)

_INITIAL_BOOKS = [
    {
        'pk': 'getting-things-done',
        'title': 'Getting Things Done',
        'author': 'David Allen',
        'status': 'read',
        'reflection': 'A practical system for managing everything on your plate.',
    },
    {
        'pk': 'leadershift',
        'title': 'Leadershift',
        'author': 'John C. Maxwell',
        'status': 'read',
        'reflection': 'How to continuously adapt and grow as a leader.',
    },
]


@books_bp.route('/books')
def books():
    try:
        track_visit('books')
    except Exception:
        pass
    try:
        all_books = scan_table('books') or []
    except Exception:
        all_books = []
    # Auto-seed missing books
    existing_pks = {b['pk'] for b in all_books if 'pk' in b}
    for book in _INITIAL_BOOKS:
        if book['pk'] not in existing_pks:
            try:
                put_item('books', book)
            except Exception:
                pass
            all_books.append(book)
    # Fallback: if still empty, use initial books directly
    if not all_books:
        all_books = _INITIAL_BOOKS
    currently_reading = [b for b in all_books if b.get('status') == 'reading']
    have_read = [b for b in all_books if b.get('status') == 'read']
    return render_template('books.html',
                           currently_reading=currently_reading,
                           have_read=have_read)
