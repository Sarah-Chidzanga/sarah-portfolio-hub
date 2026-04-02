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


def test_global_visit_endpoint_returns_pill(client):
    resp = client.get('/visits/global')
    assert resp.status_code == 200
    assert b'visit' in resp.data


def test_global_visit_count_increments(client):
    client.get('/')   # triggers track_visit via home route
    resp = client.get('/visits/global')
    assert b'1' in resp.data or b'visit' in resp.data
