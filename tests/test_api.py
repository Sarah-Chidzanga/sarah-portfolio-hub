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


def test_meta_returns_json(client):
    resp = client.get('/meta')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'version' in data
    assert 'commit_sha' in data
    assert 'deploy_timestamp' in data


def test_about_returns_json(client):
    resp = client.get('/about')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['name'] == 'Sarah Chidzanga'
    assert 'skills' in data
    assert 'currently_learning' in data


def test_fun_fact_returns_fact(client):
    resp = client.get('/fun-fact')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'fact' in data
    assert len(data['fact']) > 10


def test_contact_post_valid(client):
    resp = client.post('/contact', json={
        'name': 'Alice',
        'email': 'alice@example.com',
        'message': 'Hello Sarah!',
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['ok'] is True


def test_contact_post_missing_fields(client):
    resp = client.post('/contact', json={'name': 'Alice'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
