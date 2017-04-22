# coding=utf-8
from __future__ import absolute_import, print_function

import logging
import re

import boto3

DYNAMODB_ARN_REGEX = re.compile(r'arn:aws:dynamodb:(?P<region>[^:]+):\d+:table/(?P<table>\w+)')

def parse_dynamodb_arn(arn):
    m = DYNAMODB_ARN_REGEX.match(arn)
    try:
        d = m.groupdict()
        return d['region'], d['table']
    except (AttributeError, KeyError):
        raise ValueError("Could not parse arn: %s".format(arn))


class DBClient(object):
    def __init__(self, arn, primary_key='Key',
            access_key=None, access_secret=None, logger=None):
        if logger is None:
            logger = logging.getLogger(__name__)
        self._logger = logger.getChild(self.__class__.__name__)
        self.primary_key = primary_key
        try:
            region_name, table_name = parse_dynamodb_arn(arn)
        except ValueError as e:
            self._logger.error(e)
            raise
        self.table_name = table_name
        self._client = boto3.client(
            'dynamodb',
            region_name=region_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=access_secret
        )

    def batch_write(self, data):
        put_requests = []
        for key, value in data.items():
            if isinstance(value, basestring):
                value_map = {'S': value}
            elif isinstance(value, (int, long, float)):
                value_map = {'N': str(value)}
            else:
                self._logger.warn("skipping value of type %r: %r = %r", type(value), key, value)
                continue
            put_requests.append({
                'PutRequest': {
                    'Item': {
                        self.primary_key: {'S': key},
                        'Value': value_map
                    }
                }
            })

        self._logger.info("sending batch write request: %r", put_requests)
        response = self._client.batch_write_item(
            RequestItems={self.table_name: put_requests}
        )
        self._logger.info("got response: %r", response)
