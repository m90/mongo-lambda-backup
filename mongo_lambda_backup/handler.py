from os import environ
from urllib.parse import urlparse
import logging

from pymongo import MongoClient
import boto3 as boto
from bson.json_util import dumps, JSONOptions, DatetimeRepresentation

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3 = boto.resource("s3")


def handler(event, context):
    """
    Perform a complete backup of a MongoDB database to a S3 bucket. Each collection
    will be stored in a separate JSON file, as output by `mongodump`.
    Required environment values are MONGO_URI, BUCKET_NAME. Optionally
    MONGO_DATABASE, BUCKET_FOLDER and COLLECTION_BLACKLIST can be set.
    """

    temp_filepath = "/tmp/mongodump.json"
    collection_blacklist = environ.get("COLLECTION_BLACKLIST")
    bucket_folder = environ.get("BUCKET_FOLDER", "backups")
    bucket_name = environ["BUCKET_NAME"]
    db_uri = environ["MONGO_URI"]

    db_name = environ.get("MONGO_DATABASE")
    if db_name is None:
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
    for collection_name in eligible_collections:
        with open(temp_filepath, "w") as f:
            for doc in database.get_collection(collection_name).find():
                f.write(dumps(doc, json_options=json_options) + "\n")

        s3.Bucket(bucket_name).upload_file(
            temp_filepath, "{}/{}.json".format(bucket_folder, collection_name)
        )
