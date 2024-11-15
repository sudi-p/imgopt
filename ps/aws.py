import boto3
import os
from botocore.exceptions import NoCredentialsError
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name='us-west-1',
    aws_access_key_id='AKIAYLRCW5Z53MCRUCWB',
    aws_secret_access_key='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',
    config=boto3.session.Config(signature_version='v4')
)

# Bucket name
bucket = 'unboxme'

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
            ExpiresIn=3600
        )
        logger.info(f"Fetched final url, {url}")
        return url
    except NoCredentialsError:
        print("Credentials not available")
        return None

# Get signed URL for uploading an object
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
def list_bucket_contents():
    bucket_name = 'unboxme'
    prefix = 'Outputs/'
    try:
        # Attempt to list objects in the specified bucket and prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' in response:
            print(f"Contents of bucket '{bucket_name}' under prefix '{prefix}':")
            for obj in response['Contents']:
                print(" -", obj['Key'])  # Print each file's key
        else:
            print("No objects found in the specified bucket and prefix.")
            
    except NoCredentialsError:
        print("Credentials not available or are incorrect.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except Exception as e:
        print(f"Error accessing bucket: {e}")

# Run the function to list bucket contents

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
          
          ExpiresIn=3600
        )
        list_bucket_contents()
        return response
    except NoCredentialsError:
        print("Credentials not available")
        return None
