import sys
sys.path.append('../..')

import os
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


def main(event, context):
    table = os.environ['USER_DECKS_TABLE']
    cards_table = os.environ['GLOBAL_CARDS_TABLE']

    try:
        Key = {
            'userId': event['requestContext']['identity']['cognitoIdentityId'],
            'deckId': event['pathParameters']['id']
        }
        result = dynamodb_lib.call(table, 'get_item', Key)

        # Get deck stats if on analyze page
        if event['queryStringParameters']['analyze']:
            # parse cards from deck list txt
            

            try:
                input_id = event['requestContext']['identity']['cognitoIdentityId']

                params = {
                    'KeyConditionExpression': Key('userId').eq(input_id)
                }
                result = dynamodb_lib.call(cards_table, 'query', params)

                response = success(result['Items'])
            except:
                response = failure({'status': False})

        response = success(result['Item'])
    except:
        response = failure({'status': False, 'error': 'Item not found.'})

    return response
