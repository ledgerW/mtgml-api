import sys
sys.path.append('../..')

import os
import json
import stripe
import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure
from libs.payment_lib import *


def main(event, context):
    stripe.api_key = os.environ['STRIPE_SECRET_KEY']
    endpoint_secret = os.environ['STRIPE_SIGNING_SECRET']

    payload = event['body']
    sig_header = event['headers']['Stripe-Signature']
    data = None

    try:
        data = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as e:
        return failure(400, {'message': 'failure'})
    except Exception as e:
        return failure(400, {'message': 'failure'})

    if data['type'] == 'checkout.session.completed':
        session = data['data']['object']

        # SAVE CUSTOMER AND SUBSCRIPTION ID TO A NEW DYNAMO TABLE
        # cust_id = session['customer']
        # sub_id = session['subscription']

    return success({'session':session})
