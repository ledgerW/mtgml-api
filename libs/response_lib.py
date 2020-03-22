import json
from decimal import Decimal

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": True
}

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, Decimal):
        if float(obj).is_integer():
            return int(obj)
        else:
            return float(obj)
    raise TypeError


def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body, default=set_default)
    }
    

def success(body):
    return build_response(200, body)


def failure(status=500, body=None):
    return build_response(status, body)
