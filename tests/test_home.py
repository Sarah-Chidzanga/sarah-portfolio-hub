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
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_home_returns_200(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Sarah' in resp.data


def test_post_comment_returns_comment_list(client):
    resp = client.post('/comment/home', data={'author': 'Alice', 'body': 'Hello!'})
    assert resp.status_code == 200
    assert b'Alice' in resp.data
    assert b'Hello!' in resp.data


def test_post_empty_comment_ignored(client):
    resp = client.post('/comment/home', data={'author': 'Alice', 'body': ''})
    assert resp.status_code == 204


def test_like_home_returns_button(client):
    resp = client.post('/like/home/home')
    assert resp.status_code == 200
    assert b'liked' in resp.data
