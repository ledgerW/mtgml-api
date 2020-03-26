import sys
sys.path.append('../..')

import os
from collections import Counter
import pandas as pd
import libs.dynamodb_lib as dynamodb_lib
from boto3.dynamodb.conditions import Key, Attr

TYPES = ['Land','Creature','Enchantment','Sorcery','Instant','Artifact','Planeswalker']


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

    atts_to_get = "cardId, power, toughness, #ci, colors, #n, #mc, #s, #sn, #tl, rarity, #ot, #iu, prices, #pu, legalities, #cf"
    proj_expr = {"#n":"name", "#ci":"color_identity", "#mc":"mana_cost", "#s":"set", "#sn":"set_name", "#tl":"type_line", "#ot":"oracle_text", "#iu":"image_uris", "#pu":"purchase_uris", "#cf":"card_faces"}


    params = {
        'IndexName': 'lang-name-index',
        'KeyConditionExpression': Key('lang').eq('en') & Key('name').eq(card['name']),
        'FilterExpression': Attr('set').eq(card['set']),
        'ProjectionExpression': atts_to_get,
        'ExpressionAttributeNames': proj_expr
    }

    result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'lang-name-index',
            'KeyConditionExpression': Key('lang').eq('en') & Key('name').eq(card['name']),
            'ProjectionExpression': atts_to_get,
            'ExpressionAttributeNames': proj_expr
        }

        result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'lang-name-index',
            'KeyConditionExpression': Key('lang').eq('en') & Key('name').begins_with(card['name']),
            'FilterExpression': Attr('set').eq(card['set']),
            'ProjectionExpression': atts_to_get,
            'ExpressionAttributeNames': proj_expr
        }

        result = dynamodb_lib.call(table, 'query', params)

    if len(result['Items']) < 1:
        params = {
            'IndexName': 'lang-name-index',
            'KeyConditionExpression': Key('lang').eq('en') & Key('name').begins_with(card['name']),
            'ProjectionExpression': atts_to_get,
            'ExpressionAttributeNames': proj_expr
        }

        result = dynamodb_lib.call(table, 'query', params)

    # These are Adventure cards
    if 'oracle_text' not in result['Items'][0]:
        txt1 = result['Items'][0]['card_faces']['0']['oracle_text']
        txt2 = result['Items'][0]['card_faces']['1']['oracle_text']
        result['Items'][0]['oracle_text'] = '{} // {}'.format(txt1, txt2)
        result['Items'][0].pop('card_faces')

    try:
        result['Items'][0]['mana_cost'] = get_mana_cost(result['Items'][0]['mana_cost'])
    except:
        result['Items'][0]['mana_cost'] = [{'W':0, 'B':0, 'R':0, 'G':0, 'U':0,
                                            'X':0, 'N':0, 'D':0, 'tot':0}]

    result['Items'][0]['type'] = parse_type_line(result['Items'][0]['type_line'])

    return result['Items'][0]


def get_mana_cost(mana_cost):
    cost = []
    mana_cost = mana_cost.replace(' ','').split('//') # in case it's an Adventure card

    for face_cost in mana_cost:
        this_cost = {'W':0, 'B':0, 'R':0, 'G':0, 'U':0,
                     'X':0, 'N':0, 'D':0, 'tot':0}
        face_cost = face_cost.replace('}{','-').replace('}','').replace('{','').split('-')
        for col in face_cost:
            if col.isdigit():
                this_cost['N'] = int(col)
            elif '/' in col:
                this_cost['D'] = this_cost['D'] + 1
            else:
                this_cost[col] = this_cost[col] + 1
        this_cost['tot'] = sum([int(amt) if amt.isdigit() else 1 for amt in face_cost])
        cost.append(this_cost)

    return cost


def parse_type_line(type_line):
    taxonomy = Counter()

    for type in TYPES:
        taxonomy[type] += 1 if type in type_line else taxonomy[type]

    return taxonomy


def get_mana_curve(cards):
    #mana_curve = [[cost['tot']]*int(card['n']) for card in cards for cost in card['data']['mana_cost']]
    mana_curve = [[cost['tot']]*int(n) for n, mana in zip(cards.n, cards.mana_cost) for cost in mana]
    mana_curve = [cost for n in mana_curve for cost in n]
    mana_curve = [cost if cost <= 6 else 6 for cost in mana_curve]
    mana_curve = pd.Series(mana_curve).value_counts().to_dict()
    for cost in range(7):
        mana_curve[cost] = 0 if cost not in mana_curve.keys() else mana_curve[cost]

    return {str(key): int(val) for key, val in mana_curve.items()}


def get_deck_profile(cards):
    profile = {}

    cards_data = [card['data'] for card in cards]
    cards_df = pd.DataFrame(cards_data)
    cards_df['n'] = [card['n'] for card in cards]
    for col in cards_df.columns:
        if isinstance(cards_df[col][0], dict):
            cards_df = pd.concat([cards_df.drop([col], axis=1), cards_df[col].apply(pd.Series)], axis=1)

    for col in cards_df.columns:
        if isinstance(cards_df[col][0], set):
            cards_df[col] = cards_df[col].apply(list)

    # Get Mana Curves
    for type in ['All', 'Creature', 'NonCreature']:
        if type == 'All':
            profile['{}_mana_curve'.format(type)] = get_mana_curve(cards_df[['n','mana_cost']])
        elif type == 'Creature':
            profile['{}_mana_curve'.format(type)] = get_mana_curve(cards_df.loc[cards_df['Creature']>0, ['n','mana_cost']])
        else:
            profile['{}_mana_curve'.format(type)] = get_mana_curve(cards_df.loc[cards_df['Creature']==0, ['n','mana_cost']])

    # Next
    n = cards_df[['n']].values.astype(int)
    types = cards_df[TYPES]
    profile['type_curve'] = (types * n).sum(axis=0).to_dict()
    #print(profile)

    return profile
