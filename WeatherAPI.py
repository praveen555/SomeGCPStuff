import requests
import logging
from google.cloud import secretmanager
import google_crc32c
import os
from dotenv import load_dotenv
load_dotenv()

## initialize the logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='applogs.log', encoding='utf-8', level=logging.DEBUG)

## initliaze gcp projects and secret name
gcp_project=os.getenv("PROJECT_ID")
api_key=os.getenv("SECRET_NAME")
api_endpoint=os.getenv("API_ENDPOINT")


def access_secret_version(secret_id: str,project_id : str, version_id="latest") -> str:

    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").

    Returns a str value of the response which can be used.
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"


    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        logger.info("Data corruption detected.")
        return response

    payload = response.payload.data.decode("UTF-8")
    logger.info(f"Secret retrived successfully for {name}")
    return payload


def weather_client(city : str,) -> dict:
    """  
    
    a simple weather api which connects to the api and returns a response
    
    """

    url_api_key=access_secret_version(api_key,gcp_project)
    url=access_secret_version(api_endpoint,gcp_project)
    weather_client=requests.get(url,params={'q':{city},'appid':{url_api_key}},timeout=10)
    try:
        if weather_client.status_code==200:
                logger.info("Connected and retrived data")
                payload=weather_client.json()
                return payload
    except Exception as e:
        logger.info(f"Failed to connect {e}")
        return e



r=weather_client("Toronto")
print(r)