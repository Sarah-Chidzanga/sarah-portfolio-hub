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
        # Seed a project
        ddb.Table('projects').put_item(Item={
            'pk': 'jamf-splunk',
            'title': 'Jamf → Splunk Integration',
            'description': 'Sends Jamf events to Splunk.',
            'category': 'jamf',
            'tech_stack': ['Python', 'Lambda', 'Splunk'],
            'current_phase': 'Build',
            'phases': {'Discovery': 'Identified data gaps.', 'Build': 'Lambda pipeline.'},
            'like_count': 3,
            'created_at': '2024-01-01T00:00:00',
        })
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_projects_list_returns_200(client):
    resp = client.get('/projects')
    assert resp.status_code == 200
    assert b'Jamf' in resp.data


def test_projects_filter_by_category(client):
    resp = client.get('/projects?category=mcri')
    assert resp.status_code == 200


def test_project_detail_returns_200(client):
    resp = client.get('/projects/jamf-splunk')
    assert resp.status_code == 200
    assert b'Splunk' in resp.data


def test_project_detail_404_for_unknown(client):
    resp = client.get('/projects/does-not-exist')
    assert resp.status_code == 404


def test_like_project_returns_button(client):
    resp = client.post('/like/project/jamf-splunk')
    assert resp.status_code == 200
    assert b'liked' in resp.data


def test_comment_on_project(client):
    resp = client.post('/comment/project/jamf-splunk',
                       data={'author': 'Bob', 'body': 'Great work!'})
    assert resp.status_code == 200
    assert b'Bob' in resp.data
