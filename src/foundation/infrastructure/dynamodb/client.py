import boto3
from foundation.core.config import settings

def get_dynamodb_resource():
    return boto3.resource('dynamodb', region_name=settings.REGION_NAME)

def get_table():
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.TABLE_NAME)
