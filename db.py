import os
import boto3
from boto3.dynamodb.conditions import Key


def _table(name):
    """Create a fresh DynamoDB Table resource. Not cached so moto works in tests."""
    return boto3.resource(
        'dynamodb',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    ).Table(name)


def get_item(table_name, pk, sk=None):
    """Return a single item by pk (and optional sk), or None if not found."""
    key = {'pk': pk}
    if sk is not None:
        key['sk'] = sk
    response = _table(table_name).get_item(Key=key)
    return response.get('Item')


def put_item(table_name, item):
    """Write an item, overwriting any existing item with the same key."""
    _table(table_name).put_item(Item=item)


def increment_counter(table_name, pk, attribute='count'):
    """Atomically add 1 to a Number attribute. Creates the item/attribute if absent."""
    response = _table(table_name).update_item(
        Key={'pk': pk},
        UpdateExpression='ADD #attr :inc',
        ExpressionAttributeNames={'#attr': attribute},
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='UPDATED_NEW',
    )
    return int(response['Attributes'][attribute])


def increment_like(table_name, pk):
    """Atomically increment like_count for an item. Returns new count."""
    return increment_counter(table_name, pk, 'like_count')


def track_visit(page_name):
    """Increment both the page-specific counter and the global total."""
    increment_counter('page_visits', page_name)
    increment_counter('page_visits', 'global')


def get_global_visit_count():
    """Return the total visit count across all pages."""
    item = get_item('page_visits', 'global')
    return int(item['count']) if item else 0


def query_items(table_name, pk, scan_index_forward=True, limit=50):
    """Query all items with a given pk, sorted by sk. Pass scan_index_forward=False for newest-first."""
    response = _table(table_name).query(
        KeyConditionExpression=Key('pk').eq(pk),
        ScanIndexForward=scan_index_forward,
        Limit=limit,
    )
    return response.get('Items', [])


def scan_table(table_name):
    """Return all items in a table (use for small tables like books, projects)."""
    response = _table(table_name).scan()
    return response.get('Items', [])
