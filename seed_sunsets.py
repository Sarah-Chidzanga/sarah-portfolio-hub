import os
import sys

os.environ.setdefault('AWS_DEFAULT_REGION', 'us-east-1')
sys.path.insert(0, os.path.dirname(__file__))

from db import put_item

sunsets = [
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

if __name__ == '__main__':
    for sunset in sunsets:
        put_item('sunset_photos', sunset)
        print(f"Added: {sunset['location']}")
    print("Done — 4 sunsets seeded.")
