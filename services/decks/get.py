import sys
sys.path.append('../..')

import os
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(event, context):
    table = os.environ['USER_DECKS_TABLE']
    cards_table = os.environ['GLOBAL_CARDS_TABLE']

    try:
        Key = {
            'userId': event['requestContext']['identity']['cognitoIdentityId'],
            'deckId': event['pathParameters']['id']
        }
        result = dynamodb_lib.call(table, 'get_item', Key)
        response = success(result['Item'])
    except:
        e = sys.exc_info()[0]
        logger.info(e)
        response = failure({'status': False, 'error': 'Deck not found.'})

    return response
