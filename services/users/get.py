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
        response = failure({'status': False, 'error': 'Item not found.'})

    return response
