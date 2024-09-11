import boto3
import os
from botocore.exceptions import NoCredentialsError
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name='us-east-2',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    config=boto3.session.Config(signature_version='s3v4')
)

# Bucket name
bucket = 'image-opt'

# Get signed URL for downloading an object
def get_signed_download_url(path):
    try:
        logger.info("Fetching Final URL")
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': path
            },
            ExpiresIn=13600
        )
        logger.info(f"Fetched final url, {url}")
        return url
    except NoCredentialsError:
        print("Credentials not available")
        return None

# Get signed URL for uploading an object
def get_signed_upload_url(path):
    try:
        # response = s3_client.generate_presigned_post(
        #     Bucket=bucket,
        #     Key=path,
        #     ExpiresIn=43600
        # )
        response = s3_client.generate_presigned_url('put_object',
          Params={
              'Bucket': bucket,
              'Key': path,
          },
          ExpiresIn=43600
        )
        return response
    except NoCredentialsError:
        print("Credentials not available")
        return None
