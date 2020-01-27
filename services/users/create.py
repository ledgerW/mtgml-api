import sys
sys.path.append('../..')

import json
import os
import datetime
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


def main(event, context):
    table = os.environ['USERS_TABLE']

    try:
        data = json.loads(event['body'])
        Item = {
                'userId': event['requestContext']['identity']['cognitoIdentityId'],
                'email': data['email'] if data['email'] != '' else None,
                'userName': data['userName'] if data['userName'] != '' else None,
                'arenaName': data['arenaName'] if data['arenaName'] != '' else None,
                'profilePic': 'default',
                'createdAt': str(datetime.datetime.now())
        }
        _ = dynamodb_lib.call(table, 'put_item', Item)

        response = success(Item)
    except:
        response = failure({'status': False})

    return response
