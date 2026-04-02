import pytest
import os
from moto import mock_aws
import boto3
from tests.conftest import TABLE_SCHEMAS


@pytest.fixture(autouse=True)
def setup_env():
    os.environ.update({
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'AWS_REGION': 'us-east-1',
    })


@pytest.fixture
def client():
    with mock_aws():
        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        for schema in TABLE_SCHEMAS:
            ddb.create_table(**schema)
        ddb.Table('sunset_photos').put_item(Item={
            'pk': 'sunset-vic-falls-01',
            'location': 'Victoria Falls',
            'story': 'Golden hour over the falls.',
            's3_url': 'https://example.com/photo.jpg',
            'taken_at': '2023-06-15',
            'like_count': 7,
            'created_at': '2023-06-15T18:00:00',
        })
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_sunsets_returns_200(client):
    resp = client.get('/sunsets')
    assert resp.status_code == 200
    assert b'Victoria Falls' in resp.data


def test_like_photo_returns_button(client):
    resp = client.post('/like/photo/sunset-vic-falls-01')
    assert resp.status_code == 200
    assert b'liked' in resp.data


def test_comment_on_photo(client):
    resp = client.post('/comment/photo/sunset-vic-falls-01',
                       data={'author': 'Eve', 'body': 'Stunning!'})
    assert resp.status_code == 200
    assert b'Eve' in resp.data


def test_photo_comments_endpoint(client):
    resp = client.get('/sunsets/sunset-vic-falls-01/comments')
    assert resp.status_code == 200
