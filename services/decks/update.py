import sys
sys.path.append('../..')

import json
import os
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


def main(event, context):
    try:
        table = os.environ['USER_DECKS_TABLE']
        data = json.loads(event['body'])

        params = {
            'Key': {
                'userId': event['requestContext']['identity']['cognitoIdentityId'],
                'deckId': event['pathParameters']['id']
            },
            'UpdateExpression': 'SET content = :content, attachment = :attachment',
            'ExpressionAttributeValues': {
                ':attachment': data['attachment'],
                ':content': data['content']
            },
            'ReturnValues': 'ALL_NEW'
        }
        result = dynamodb_lib.call(table, 'update_item', params)

        response = success({'status': True})
    except:
        response = failure({'status': False})

    return response
