import sys
sys.path.append('../..')

import os
import json
import stripe
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure
from libs.payment_lib import *


def main(event, context):
    data = json.loads(event['body'])
    storage = data['storage']
    token = data['source']
    amount = calculate_cost(storage)
    description = 'Test charge'

    stripe.api_key = os.environ['STRIPE_SECRET_KEY']

    try:
        charge = stripe.Charge.create(amount=amount,
                                      currency='usd',
                                      description=description,
                                      source=token)

        return success({'status': True})
    except Exception as e:
        return failure({'message': e.message})
