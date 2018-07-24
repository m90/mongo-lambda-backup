import unittest
from unittest.mock import patch
from os import environ
from json import loads

import boto3 as boto
from moto import mock_s3
from mongomock import MongoClient as MockMongoClient

from mongo_lambda_backup.handler import handler


def test_ok():
    assert True


@patch.dict(
    environ,
    {"BUCKET_NAME": "mongo-lambda-backup", "MONGO_URI": "mongodb://localhost/test-db"},
)
@mock_s3
class TestHandler(unittest.TestCase):
    def setUp(self):
        self.conn = boto.resource("s3", region_name="eu-central-1")
        self.conn.create_bucket(Bucket="mongo-lambda-backup")

        self.client = MockMongoClient("mongodb://localhost")
        database = self.client.get_database("test-db")
        database.create_collection("unittest")
        database["unittest"].insert_one({"this": "is", "data": ["some"]})
        database["unittest"].insert_one({"this": "is", "data": ["other"]})

    @patch("mongo_lambda_backup.handler.MongoClient")
    def test_handler(self, mock_constructor):
        mock_constructor.return_value = self.client

        handler(None, None)

        body = (
            self.conn.Object("mongo-lambda-backup", "backups/unittest.json")
            .get()["Body"]
            .read()
            .decode("utf-8")
        )
        for line in body.split("\n"):
            if line:
                doc = loads(line)
                assert doc.get("_id")
                assert doc.get("this")
                assert doc.get("data")
