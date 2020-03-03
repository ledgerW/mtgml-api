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
                'userId': event['queryStringParameters']['email']
            }
            result = dynamodb_lib.call(table, 'get_item', Key)

            data = result['Item']
            data['userId'] = event['requestContext']['identity']['cognitoIdentityId']

            # insert new item with final congito id
            result = dynamodb_lib.call(table, 'put_item', data)

            # now remove original entry with temp userId
            _ = dynamodb_lib.call(table, 'delete_item', Key)

            response = success(data)
        except:
            response = failure({'status': False, 'error': 'Item not found.'})

    return response
