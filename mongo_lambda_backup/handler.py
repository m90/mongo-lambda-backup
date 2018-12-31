from os import environ
from io import StringIO
import logging

from pymongo import MongoClient
import boto3 as boto
from bson.json_util import dumps, JSONOptions, DatetimeRepresentation

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3 = boto.resource("s3")

temp_filepath = "/tmp/mongodump.json"


def handler(event, context):
    """
    Perform a complete backup of a MongoDB database to a S3 bucket. Each collection
    will be stored in a separate JSON file, as output by `mongodump`.
    Required environment values are MONGO_URI, BUCKET_NAME. Optionally
    MONGO_DATABASE, BUCKET_FOLDER and COLLECTION_BLACKLIST can be set.
    """
    collection_blacklist = environ.get("COLLECTION_BLACKLIST")
    bucket_folder = environ.get("BUCKET_FOLDER", "backups")
    bucket_name = environ["BUCKET_NAME"]
    db_uri = environ["MONGO_URI"]

    if environ.get("MONGO_URI_IS_ENCRYPTED"):
        from base64 import b64decode

        kms = boto.client("kms")
        decrypted = kms.decrypt(CiphertextBlob=b64decode(db_uri))
        db_uri = decrypted["Plaintext"].decode()

    db_name = environ.get("MONGO_DATABASE")
    if db_name is None:
        from urllib.parse import urlparse

        loc = urlparse(db_uri)
        db_name = loc.path.strip("/")

    LOGGER.info(
        "Backing up collections from database %s in bucket %s", db_name, bucket_name
    )

    s3.meta.client.head_bucket(
        Bucket=bucket_name
    )  # Check that the given bucket actually exists.

    client = MongoClient(db_uri)
    database = client.get_database(db_name)

    skip = (
        [s.strip() for s in collection_blacklist.split(",")]
        if collection_blacklist
        else []
    )
    eligible_collections = [
        name for name in database.collection_names() if not name in skip
    ]

    json_options = JSONOptions(datetime_representation=DatetimeRepresentation.ISO8601)

    def write_all_docs(collection_name, writer):
        for doc in database.get_collection(collection_name).find():
            writer.write(dumps(doc, json_options=json_options) + "\n")

    for collection_name in eligible_collections:
        if environ.get("IN_MEMORY"):
            writer = StringIO()
            write_all_docs(collection_name, writer)

            s3.Bucket(bucket_name).put_object(
                Body=writer.getvalue().encode(),
                Key="{}/{}.json".format(bucket_folder, collection_name),
            )

        else:
            with open(temp_filepath, "w") as writer:
                write_all_docs(collection_name, writer)

            s3.Bucket(bucket_name).upload_file(
                temp_filepath, "{}/{}.json".format(bucket_folder, collection_name)
            )

        LOGGER.info("Done backing up collection {}".format(collection_name))
