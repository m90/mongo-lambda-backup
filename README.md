# mongo-lambda-backup
[![Build Status](https://travis-ci.org/m90/mongo-lambda-backup.svg?branch=master)](https://travis-ci.org/m90/mongo-lambda-backup)
> Backup MongoDB databases using AWS Lambda functions

The code in this repo allows running the backup of a MongoDB database to S3 on AWS Lambda by emulating a `mongodump` using `pymongo` and `boto3`. By default the function will create a JSON file for every collection in the database and save them in a `/backup` folder.

## Install from pip

```
pip install mongo_lambda_backup
```

## Configuration

All configuration values are passed using environment variables.

The following values are required:

- `MONGO_URI`: The URI (including authentication credentials if needed) of the MongoDB host to be backed up. In case this **contains credentials** you can encrypt this value using AWS KMS and set `MONGO_URI_IS_ENCRYPTED` to tell the Lambda it needs to decrypt the given value.
- `BUCKET_NAME`: The name of the S3 bucket to store the backup files in.

The following values are optional:

- `MONGO_URI_IS_ENCRYPTED`: In case this environment variable is set, the handler assumes the URI (which potentially contains credentials) needs to be encrypted using the KMS key associated with the Lambda.
- `MONGO_DATABASE`: The name of the database to back up. In case this is not set, it will be read from the path of `MONGO_URI`.
- `BUCKET_FOLDER`: The folder in the bucket to store the JSON files in. Defaults to `backups`.
- `COLLECTION_BLACKLIST`: A comma-separated collection of collection names to skip when performing the back up (e.g. for skipping indices or vendor specific databases).
- `IN_MEMORY`: If set, the collection to be dumped to S3 will be handled in the Lambda's memory before writing. This might affect both backup speed as well as Lambda Limits in certain scenarios.

### License
MIT © [Frederik Ring](http://www.frederikring.com)
