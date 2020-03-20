import sys
sys.path.append('../..')

import os
import libs.dynamodb_lib as dynamodb_lib
from boto3.dynamodb.conditions import Key, Attr


def parse_deck_list(content):
    cards = []
    lines = content.split('\n')
    for line in lines:
        card = {}
        line = line.split(' ')
        if len(line) > 1:
            card['n'] = line[0]
            card['set_card_num'] = line[-1]
            card['set'] = line[-2].replace('(','').replace(')','').lower()
            card['name'] = ' '.join(line[1:-2])
            cards.append(card)

    return cards


def get_card_data(card):
    table = os.environ['GLOBAL_CARDS_TABLE']

    atts_to_get = "cardId, #ci, colors, #n, #mc, #s, #sn, #tl, rarity, #ot, #iu, prices, #pu, legalities, #cf"
    proj_expr = {"#n":"name", "#ci":"color_identity", "#mc":"mana_cost", "#s":"set", "#sn":"set_name", "#tl":"type_line", "#ot":"oracle_text", "#iu":"image_uris", "#pu":"purchase_uris", "#cf":"card_faces"}


    params = {
        'IndexName': 'name-index',
        'KeyConditionExpression': Key('name').eq(card['name']),
        'FilterExpression': Attr('lang').eq('en') & Attr('set').eq(card['set']),
        'ProjectionExpression': atts_to_get,
        'ExpressionAttributeNames': proj_expr
    }

    result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'name-index',
            'KeyConditionExpression': Key('name').eq(card['name']),
            'FilterExpression': Attr('lang').eq('en'),
            'ProjectionExpression': atts_to_get,
            'ExpressionAttributeNames': proj_expr
        }

        result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'set-name-index',
            'KeyConditionExpression': Key('set').eq(card['set']) & Key('name').begins_with(card['name']),
            'FilterExpression': Attr('lang').eq('en'),
            'ProjectionExpression': atts_to_get,
            'ExpressionAttributeNames': proj_expr
        }

        result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'set-name-index',
            'KeyConditionExpression': Key('set').eq(card['set']) & Key('name').begins_with(card['name']),
            'FilterExpression': Attr('lang').eq('en'),
            'ProjectionExpression': atts_to_get,
            'ExpressionAttributeNames': proj_expr
        }

        result = dynamodb_lib.call(table, 'query', params)

    if 'oracle_text' not in result['Items'][0]:
        txt1 = result['Items'][0]['card_faces']['0']['oracle_text']
        txt2 = result['Items'][0]['card_faces']['1']['oracle_text']
        result['Items'][0]['oracle_text'] = '{} // {}'.format(txt1, txt2)
        result['Items'][0].pop('card_faces')

    return result['Items'][0]
