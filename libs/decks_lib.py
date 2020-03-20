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


def get_card_key(card):
    table = os.environ['GLOBAL_CARDS_TABLE']
    name = card['name']
    set =  card['set']


    params = {
        'IndexName': 'name-index',
        'KeyConditionExpression': Key('name').eq(card['name']),
        'FilterExpression': Attr('lang').eq('en') & Attr('set').eq(card['set']),
        'ProjectionExpression': 'cardId'
    }

    result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'name-index',
            'KeyConditionExpression': Key('name').eq(card['name']),
            'FilterExpression': Attr('lang').eq('en'),
            'ProjectionExpression': 'cardId'
        }

        result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'set-name-index',
            'KeyConditionExpression': Key('set').eq(card['set']) & Key('name').begins_with(card['name']),
            'FilterExpression': Attr('lang').eq('en'),
            'ProjectionExpression': 'cardId'
        }

        result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'set-name-index',
            'KeyConditionExpression': Key('set').eq(card['set']) & Key('name').begins_with(card['name']),
            'FilterExpression': Attr('lang').eq('en'),
            'ProjectionExpression': 'cardId'
        }

        result = dynamodb_lib.call(table, 'query', params)

    return result['Items'][0]['cardId']
