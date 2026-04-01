import pytest
from moto import mock_aws
from tests.conftest import TABLE_SCHEMAS
import boto3
import os


@pytest.fixture(autouse=True)
def setup_env():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_REGION'] = 'us-east-1'


@pytest.fixture
def tables():
    with mock_aws():
        ddb = boto3.resource('dynamodb', region_name='us-east-1')
        for schema in TABLE_SCHEMAS:
            ddb.create_table(**schema)
        yield ddb


def test_put_and_get_item(tables):
    import db
    db.put_item('projects', {'pk': 'test-project', 'title': 'Test', 'like_count': 0})
    item = db.get_item('projects', 'test-project')
    assert item['title'] == 'Test'


def test_get_item_returns_none_for_missing(tables):
    import db
    result = db.get_item('projects', 'does-not-exist')
    assert result is None


def test_increment_counter_creates_and_increments(tables):
    import db
    count = db.increment_counter('page_visits', 'home')
    assert count == 1
    count = db.increment_counter('page_visits', 'home')
    assert count == 2


def test_increment_like(tables):
    import db
    db.put_item('projects', {'pk': 'my-proj', 'like_count': 5})
    new_count = db.increment_like('projects', 'my-proj')
    assert new_count == 6


def test_track_visit_increments_page_and_global(tables):
    import db
    db.track_visit('sunsets')
    db.track_visit('sunsets')
    db.track_visit('home')
    assert db.get_global_visit_count() == 3
    page_item = db.get_item('page_visits', 'sunsets')
    assert int(page_item['count']) == 2


def test_query_items_returns_newest_first(tables):
    import db
    db.put_item('comments', {'pk': 'home', 'sk': '2024-01-01T10:00:00', 'author': 'Alice', 'body': 'first'})
    db.put_item('comments', {'pk': 'home', 'sk': '2024-01-02T10:00:00', 'author': 'Bob', 'body': 'second'})
    comments = db.query_items('comments', 'home', scan_index_forward=False)
    assert comments[0]['author'] == 'Bob'
    assert comments[1]['author'] == 'Alice'


def test_scan_table(tables):
    import db
    db.put_item('books', {'pk': 'book-1', 'title': 'Atomic Habits'})
    db.put_item('books', {'pk': 'book-2', 'title': 'Deep Work'})
    books = db.scan_table('books')
    assert len(books) == 2
