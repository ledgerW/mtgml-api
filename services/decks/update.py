import sys
sys.path.append('../..')

import json
import os
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure
from libs.decks_lib import parse_deck_list, get_card_data, get_deck_profile


def main(event, context):
    try:
        table = os.environ['USER_DECKS_TABLE']
        data = json.loads(event['body'])

        cards = parse_deck_list(data['content'])

        for i, card in enumerate(cards):
            cards[i]['data'] = get_card_data(card)

        data['profile'] = get_deck_profile(cards)
        data['cards'] = cards
        data['display'] = cards[0]['data']['image_uris']['art_crop']

        update_expression = 'SET ' + ', '.join(['{key} = :{key}'.format(key=key) for key in data.keys()])
        update_expression = update_expression.replace('name =', '#name =')

        expression_att_vals = {':{}'.format(key): data[key] for key in data.keys()}
        expression_att_names = {'#name': 'name'}

        params = {
            'Key': {
                'userId': event['requestContext']['identity']['cognitoIdentityId'],
                'deckId': event['pathParameters']['id']
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeNames': expression_att_names,
            'ExpressionAttributeValues': expression_att_vals,
            'ReturnValues': 'ALL_NEW'
        }

        result = dynamodb_lib.call(table, 'update_item', params)

        response = success({'status': True})
    except:
        response = failure({'status': False})

    return response
