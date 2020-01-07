import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch

patch(['boto3'])

def call(table, action, params):
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)

    print('in dynamodb_lib')

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
        elif action == 'batch_write_item':
            return getattr(client, action)(RequestItems=params)
    except Exception as e:
        print(e)
        xray_recorder.end_subsegment()


def batch_format(val):
    if type(val) is str:
        return {"S": str(val)} if len(val)>0 else {"NULL": True}
    if type(val) is int:
        return {"N": str(val)}
    if type(val) is float:
        return {"N": str(val)}
    if type(val) is list:
        return {"SS": val} if len(val)>0 else {"SS": ['empty']}
    if type(val) is bool:
        return {"BOOL": True}
    if val is None:
        return {"NULL": True}
    if type(val) is dict:
        return {"M": {val_key: batch_format(val_val) for val_key, val_val in val.items()}}
