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

    atts_to_get = "#n, #mc, #s, #sn, #tl, rarity, #ot, #iu, prices, #pu, legalities"
    proj_expr = {"#n":"name", "#mc":"mana_cost", "#s":"set", "#sn":"set_name", "#tl":"type_line", "#ot":"oracle_text", "#iu":"image_uris", "#pu":"purchase_uris"}

    #try:
    Key = {
        'userId': event['requestContext']['identity']['cognitoIdentityId'],
        'deckId': event['pathParameters']['id']
    }
    result = dynamodb_lib.call(table, 'get_item', Key)
    response = success(result['Item'])

    # Get deck stats if on analyze page
    if event['queryStringParameters']['analyze']:
        # parse cards from deck list txt
        deck = result['Item']['cards']

        # Bath read from Dynamo - get all cards in deck
        RequestItems = {
            cards_table: {
                'Keys': [
                    {
                      'cardId': {'S': card['cardId']}
                    } for card in deck if 'cardId' in card.keys()
                ],
                'ProjectionExpression': atts_to_get,
                'ExpressionAttributeNames': proj_expr
            }
        }

        dynamo_res = dynamodb_lib.call(table, 'batch_get_item', RequestItems)
        response = success(dynamo_res['Responses'][cards_table])

        # Get remaining cards if more than 100 or more than 16MB returned
        if len(dynamo_res['UnprocessedKeys'])>0:
            remaining_keys= [card.keys()[0] for card in dynamo_res['UnprocessedKeys'][cards_table]['Keys']]
            remaining_cards = [card for card in deck if card['cardId'] in remaining_keys]

            RequestItems = {
                cards_table: {
                    'Keys': [
                        {
                          'cardId': {'s': card.cardId}
                        } for card in remaining_cards
                    ],
                    'ProjectionExpression': atts_to_get,
                    'ExpressionAttributeNames': proj_expr
                }
            }

            remaining_res = dynamodb_lib.call(table, 'batch_get_item', RequestItems)
            response = success(dynamo_res['Responses'][cards_table] + remaining_res['Responses'][cards_table])

    #except:
    #    e = sys.exc_info()[0]
    #    logger.info(e)
    #    response = failure({'status': False, 'error': 'Item not found.'})

    return response
