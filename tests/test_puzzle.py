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
            'story': 'Golden hour.',
            's3_url': 'https://example.com/photo.jpg',
            'taken_at': '2023-06-15',
            'like_count': 0,
            'created_at': '2023-06-15T18:00:00',
        })
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_puzzle_difficulty_select(client):
    resp = client.get('/puzzle/sunset-vic-falls-01')
    assert resp.status_code == 200
    assert b'Easy' in resp.data
    assert b'Medium' in resp.data
    assert b'Hard' in resp.data


def test_puzzle_easy(client):
    resp = client.get('/puzzle/sunset-vic-falls-01/easy')
    assert resp.status_code == 200
    assert b'puzzle-board' in resp.data


def test_puzzle_medium(client):
    resp = client.get('/puzzle/sunset-vic-falls-01/medium')
    assert resp.status_code == 200
    assert b'puzzle-board' in resp.data


def test_puzzle_hard(client):
    resp = client.get('/puzzle/sunset-vic-falls-01/hard')
    assert resp.status_code == 200
    assert b'puzzle-board' in resp.data


def test_puzzle_unknown_photo(client):
    resp = client.get('/puzzle/does-not-exist')
    assert resp.status_code == 404


def test_puzzle_unknown_difficulty(client):
    resp = client.get('/puzzle/sunset-vic-falls-01/impossible')
    assert resp.status_code == 404
