import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

def call(table, action, params):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)

    try:
        xray_recorder.begin_subsegment(action)
        if action == 'put_item':
            return getattr(table, action)(Item=params)
        elif action == 'get_item' or action == 'delete_item':
            return getattr(table, action)(Key=params)
        elif action == 'query':
            return getattr(table, action)(KeyConditionExpression=params['KeyConditionExpression'])
        elif action == 'update_item':
            return getattr(table, action)(Key=params['Key'],
                                          UpdateExpression=params['UpdateExpression'],
                                          ExpressionAttributeValues=params['ExpressionAttributeValues'],
                                          ReturnValues=params['ReturnValues'])
    except:
        xray_recorder.end_subsegment()
