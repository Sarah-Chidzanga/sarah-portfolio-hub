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
