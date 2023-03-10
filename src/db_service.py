import boto3
from boto3.dynamodb.conditions import Key

import app

def get_item(key, value):
    client = boto3.resource('dynamodb')
    try:
        table = client.Table(app.ENV_TABLE_NAME)
        response = table.query(
            KeyConditionExpression=Key(key).eq(value)
        )
        items = response['Items']
        if items:
            return items[0]
        else:
            return []
    except Exception as e:
        raise RuntimeError('cannot retrieve data from db cause: ' + str(e))
