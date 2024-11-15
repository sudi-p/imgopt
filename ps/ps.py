import requests
import json
from dotenv import load_dotenv
import os
import logging
import time
import random
from loguru import logger
from urllib.parse import urlparse
from ps.aws import get_signed_download_url, get_signed_upload_url

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

def getAdobeAccessToken(PS_CLIENT_ID, PS_CLIENT_SECRET):
    token_url = 'https://ims-na1.adobelogin.com/ims/token/v3'

    params = {
        'client_id': PS_CLIENT_ID,
        'client_secret': PS_CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'openid, AdobeID, read_organizations'
    }

    try:
        response = requests.post(token_url, data=params)
        response.raise_for_status()

        data = response.json()
        return data.get('access_token')
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
    except KeyError:
        logging.error("The response did not contain an access token.")
    return None

def edit_text(token, PS_CLIENT_ID, signed_get_url, signed_post_url, title, subTitle, callout1, callout2, callout3):
    storage = 'external'

    url = "https://image.adobe.io/pie/psdService/text"
    time.sleep(2)
    headers = {
        "Authorization": f"Bearer {token}",
        "x-api-key": PS_CLIENT_ID,
        "Content-Type": "application/json"
    }

    data = {
        "inputs": [
            {
                "href": signed_get_url,
                "storage": storage
            }
        ],
        "options": {
            "layers": [
                {
                    "name": "title",
                    "text": {
                        "contents": title,
                    }
                },
                {
                    "name": "subtitle",
                    "text": {
                        "contents": subTitle,
                    }
                },
                # add more
                 {
                    "name": "callout1",
                    "text": {
                        "contents": callout1,
                    }
                },
                # add more
                 {
                    "name": "callout2",
                    "text": {
                        "contents": callout2,
                    }
                },
                # add more
                 {
                    "name": "callout3",
                    "text": {
                        "contents": callout3,
                    }
                },
            ]
        },
        "outputs": [
            {
                "href": signed_post_url,
                "overwrite": True,
                "type": "image/jpeg",
                "storage": "external"
            }  
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        data = response.json()
        logger.info(f"Response status code: {response.status_code}")
        logger.info(json.dumps(data, indent=2))
        job_url = data["_links"]["self"]["href"]
        return job_url
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response")
    except KeyError:
        logger.error("The response does not contain expected keys")
    return None

import time

def check_job_status(job_url, token, PS_CLIENT_ID, retries=50, delay=1):
    headers = {
        "Authorization": f"Bearer {token}",
        "x-api-key": PS_CLIENT_ID,
    }

    for attempt in range(retries):
        try:
            resp = requests.get(job_url, headers=headers)
            resp.raise_for_status()

            data = resp.json()
            print(json.dumps(data, indent=4))  # Print response for debugging

            # Check if 'outputs' and 'renditions' are present
            if "outputs" in data and "_links" in data["outputs"][0] and "renditions" in data["outputs"][0]["_links"]:
                output_link = data["outputs"][0]["_links"]["renditions"][0]["href"]
                return output_link
            elif data["outputs"][0]["status"] == "pending":
                print(f"Attempt {attempt + 1}: Job still pending. Retrying in {delay} seconds...")
                time.sleep(delay)
            elif data["outputs"][0]["status"] == "running":
                print(f"Attempt {attempt + 1}: Job still Running. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Unexpected job status or structure.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
    raise Exception("Job did not complete successfully within the retry limit.")


def check(token, PS_CLIENT_ID):
    check_url = "https://image.adobe.io/pie/psdService/hello"
    headers = {
        "Authorization": f"Bearer {token}",
        "x-api-key": PS_CLIENT_ID
    }

    try:
        response = requests.get(check_url, headers=headers)
        response.raise_for_status()
        logger.info(response.text)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")

def add_text(template, title, subTitle, callout1, callout2, callout3):
    PS_CLIENT_ID = os.environ['PS_CLIENT_ID']
    PS_CLIENT_SECRET = os.environ['PS_CLIENT_SECRET']

    signed_get_url = get_signed_download_url(template)
    signed_post_url = get_signed_upload_url(f'Outputs/Image{random.randint(0,1000)}.jpg')

    if signed_get_url and signed_post_url:
        # logger.info(f"Signed GET URL: {signed_get_url}")
        # logger.info(f"Signed POST URL: {signed_post_url}")

        token = getAdobeAccessToken(PS_CLIENT_ID, PS_CLIENT_SECRET)
        if token:
            check(token, PS_CLIENT_ID)
            job_url = edit_text(token, PS_CLIENT_ID, signed_get_url, signed_post_url, title, subTitle, callout1, callout2, callout3)
            logger.info("Job URL fetched")
            if job_url:
                output_s3_url = check_job_status(job_url, token, PS_CLIENT_ID)
                output_url = get_signed_download_url(output_s3_url)
                logger.info("Image presigned url", output_url)
                return output_url
        else:
            logging.error("Failed to obtain access token")
    else:
        logging.error("Failed to generate signed URLs")

from psd_tools import PSDImage
from loguru import logger

def validate_psd_structure_local(psd_path):
    """
    Validates the structure of a PSD file locally by checking for required layers.
    
    Args:
        psd_path (str): Path to the PSD file to validate.
    
    Returns:
        tuple: (bool, str) A boolean indicating success and a message.
    """
    required_layers = {"title", "subtitle", "callout1", "callout2", "callout3"}
    try:
        # Load the PSD file
        psd = PSDImage.open(psd_path)
        logger.info(f"Loaded PSD file: {psd_path}")

        # Collect layer names
        layer_names = {layer.name for layer in psd.descendants() if layer.kind == 'type'}
        logger.info(f"Found layers: {layer_names}")

        # Check for missing layers
        missing_layers = required_layers - layer_names
        if missing_layers:
            return False, f"Missing required layers: {', '.join(missing_layers)}"
        
        return True, "PSD validation successful. All required layers are present."
    
    except Exception as e:
        logger.error(f"Error validating PSD structure: {e}")
        return False, f"Error occurred while validating PSD: {e}"

