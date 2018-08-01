import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mongo_lambda_backup",
    version="0.1.0",
    author="Frederik Ring",
    author_email="frederik.ring@gmail.com",
    description="Backup MongoDB databases using AWS Lambda functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m90/mongo-lambda-backup",
    packages=["mongo_lambda_backup"],
    install_requires=["boto3~=1.7.62", "pymongo~=3.7.1"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
