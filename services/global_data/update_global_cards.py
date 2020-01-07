import sys
sys.path.append('../..')

import os
import boto3
import json
import requests
import math
from time import sleep
import pandas as pd
import numpy as np
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import libs.dynamodb_lib as dynamodb_lib
from libs.response_lib import success, failure


CARDS_URL = 'https://api.scryfall.com/cards?page={}'
CARDS_PER_PAGE = 175
PAGES_PER_WORKER = 100
BATCH_LIMIT = 25

client = boto3.client('lambda')


def save_scryfall_page(table, page):
    dynamo_batches = [(first, first+BATCH_LIMIT) for first in list(range(0, CARDS_PER_PAGE, BATCH_LIMIT))]

    if page % 10 == 0 or page==1:
        print('page in scryfall saver: {}'.format(page))
        logger.info(print('page in scryfall saver: {}'.format(page)))

    res = requests.get(CARDS_URL.format(page))
    for batch in dynamo_batches:
        cards = res.json()['data'][batch[0]:batch[1]]
        for idx, card in enumerate(cards):
            for key, val in card.items():
                cards[idx][key] = dynamodb_lib.batch_format(val)
            cards[idx]['cardId'] = cards[idx]['id']

        # Save to Dynamo
        RequestItems = {
            table: [
                {
                    'PutRequest': {
                        'Item': card
                    }
                } for card in cards
            ]
        }
        dynamo_res = dynamodb_lib.call(table, 'batch_write_item', RequestItems)
    return res.json()['has_more']


def master(event, context):
    '''
    Trigger: Cron event
    Call Scryfall.com to check number of cards and then distribute
    # collection to worker function below
    '''
    res = requests.get(CARDS_URL.format(1))

    total_cards = res.json()['total_cards']
    total_pages = math.ceil(total_cards / CARDS_PER_PAGE)

    worker_pages = [(first, first+PAGES_PER_WORKER) for first in list(range(1, total_pages+1, PAGES_PER_WORKER))]

    for pages in worker_pages:
        logger.info(pages)
        response = client.invoke(
            FunctionName='mtgml-global-data-{}-cards_worker'.format(os.environ['stage']),
            Payload=json.dumps({"first": pages[0], "last": pages[1]}))

        logger.info(response)


def worker(event, context):
    '''
    Trigger: http post from master
    Accept range of scryfall pages to collect from master,
    call each page,
    then collect them and load to GLOBAL_CARDS_TABLE
    '''
    print(event)
    logger.info(event)
    try:
        table = os.environ['GLOBAL_CARDS_TABLE']
        pages = event

        # Get cards from Scryfall
        for page in range(pages['first'], pages['last']):
            if has_more:
                sleep(0.1)
                has_more = save_scryfall_page(table, page)

        response = success({'status': True})
    except:
        response = failure({'status': False})

    return response
