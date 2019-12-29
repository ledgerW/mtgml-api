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
    plan = data['plan']
    domain = data['domain']

    stripe.api_key = os.environ['STRIPE_SECRET_KEY']

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            subscription_data={
            'items': [{
                'plan': plan,}],
            },
            success_url='{}settings'.format(domain),
            cancel_url='{}'.format(domain),
        )

        return success({'session':session})
    except Exception as e:
        return failure({'message': e.message})
