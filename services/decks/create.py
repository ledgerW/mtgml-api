import sys
sys.path.append('../..')

import json
import os
import uuid
import datetime
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure
from libs.decks_lib import parse_deck_list, get_card_key


def main(event, context):
    table = os.environ['USER_DECKS_TABLE']

    try:
        data = json.loads(event['body'])

        cards = parse_deck_list(data['content'])

        for i, card in enumerate(cards):
            cards[i]['cardId'] = get_card_key(card)

        Item = {
                'userId': event['requestContext']['identity']['cognitoIdentityId'],
                'deckId': str(uuid.uuid1()),
                'name': data['name'],
                'content': data['content'],
                'cards': cards,
                'attachment': data['attachment'],
                'createdAt': str(datetime.datetime.now())
        }

        _ = dynamodb_lib.call(table, 'put_item', Item)

        response = success(Item)
    except:
        response = failure({'status': False})

    return response
