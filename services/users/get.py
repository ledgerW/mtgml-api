import sys
sys.path.append('../..')

import os
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


def main(event, context):
    table = os.environ['USERS_TABLE']

    try:
        Key = {
            'userId': event['requestContext']['identity']['cognitoIdentityId']
        }
        result = dynamodb_lib.call(table, 'get_item', Key)

        response = success(result['Item'])
    except:
        try:
            Key = {
                'email': event['queryStringParameters']['email']
            }
            result = dynamodb_lib.call(table, 'get_item', Key)

            data = result['Item']

            data['userId'] = event['requestContext']['identity']['cognitoIdentityId']

            update_expression = 'SET ' + ', '.join(['{key} = :{key}'.format(key=key) for key in data.keys()])
            expression_att_vals = {':{}'.format(key): data[key] for key in data.keys()}

            params = {
                'Key': {
                    'email': event['queryStringParameters']['email']
                },
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_att_vals,
                'ReturnValues': 'ALL_NEW'
            }
            result = dynamodb_lib.call(table, 'update_item', params)

            response = success(result['Item'])
        except:
            response = failure({'status': False, 'error': 'Item not found.'})

    return response
