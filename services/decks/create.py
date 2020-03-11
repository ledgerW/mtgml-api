import sys
sys.path.append('../..')

import json
import os
import uuid
import datetime
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


def main(event, context):
    table = os.environ['USER_DECKS_TABLE']

    try:
        data = json.loads(event['body'])
        Item = {
                'userId': event['requestContext']['identity']['cognitoIdentityId'],
                'deckId': str(uuid.uuid1()),
                'name': data['name'],
                'content': data['content'],
                'attachment': data['attachment'],
                'createdAt': str(datetime.datetime.now())
        }
        _ = dynamodb_lib.call(table, 'put_item', Item)

        response = success(Item)
    except:
        response = failure({'status': False})

    return response
