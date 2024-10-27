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

def edit_text(token, PS_CLIENT_ID, signed_get_url, signed_post_url, title, subTitle):
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

def check_job_status(job_url, token, PS_CLIENT_ID):
    headers = {
        "Authorization": f"Bearer {token}",
        "x-api-key": PS_CLIENT_ID,
    }
    time.sleep(3)
    # status = ""
    # while status not in ['succeeded', 'failed']:
    try:
        resp = requests.get(job_url, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        print(json.dumps(data, indent=4))
        output_link = data["outputs"][0]["_links"]["renditions"][0]["href"]
        parsed_url = urlparse(output_link)

        # Extract the base URL
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        start_pos = base_url.find("Outputs")

        # Extract the path using string slicing
        if start_pos != -1:
            path = base_url[start_pos:]
        else:
            path = None
        logger.info(f"Base url: {path}")
        return path
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        # break
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response")
        # break

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

def add_text(template, title, subTitle):
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
            job_url = edit_text(token, PS_CLIENT_ID, signed_get_url, signed_post_url, title, subTitle)
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

