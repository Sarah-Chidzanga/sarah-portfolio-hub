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


def test_resume_returns_200(client):
    resp = client.get('/resume')
    assert resp.status_code == 200


def test_resume_contains_education(client):
    resp = client.get('/resume')
    assert b'MCRI' in resp.data


def test_resume_contains_certifications(client):
    resp = client.get('/resume')
    assert b'Swift' in resp.data


def test_resume_contains_languages(client):
    resp = client.get('/resume')
    assert b'Shona' in resp.data
