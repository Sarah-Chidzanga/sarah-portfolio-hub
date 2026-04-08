import os
import sys

os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')
sys.path.insert(0, os.path.dirname(__file__))

from db import put_item

books = [
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

if __name__ == '__main__':
    for book in books:
        put_item('books', book)
        print(f"Added: {book['title']} — {book['author']}")
    print("Done — 2 books seeded.")
