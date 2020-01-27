import sys
sys.path.append('../..')

import json
import os
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


def main(event, context):
    try:
        table = os.environ['USERS_TABLE']
        data = json.loads(event['body'])

        update_expression = 'SET ' + ', '.join(['{key} = :{key}'.format(key=key) for key in data.keys()])
        expression_att_vals = {':{}'.format(key): data[key] for key in data.keys()}

        params = {
            'Key': {
                'userId': event['requestContext']['identity']['cognitoIdentityId']
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_att_vals,
            'ReturnValues': 'ALL_NEW'
        }
        result = dynamodb_lib.call(table, 'update_item', params)

        response = success({'status': True})
    except:
        response = failure({'status': False})

    return response
