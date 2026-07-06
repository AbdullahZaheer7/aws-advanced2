import os
import json
import time
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

# Environment variable set in Lambda configuration
BUCKET_NAME = os.environ.get("BUCKET_NAME", "")

# Images live under this prefix in the private bucket
IMAGES_PREFIX = "images/"

# 5 minutes = 300 seconds
URL_EXPIRATION_SECONDS = 300


def _response(status_code: int, body: dict):
    """Create an API Gateway compatible response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    """
    Receives POST {"imageName":"annual-meetup.jpg"}
    and returns a pre-signed URL valid for 300 seconds.

    Expected output:
      {"url": "presigned-url", "expires": <epoch seconds>}
    """

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {"ok": True})

    if not BUCKET_NAME:
        return _response(500, {"error": "BUCKET_NAME environment variable is not set"})

    # API Gateway (Lambda proxy) typically forwards JSON body under event['body']
    image_name = None
    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body) if body else {}
        if isinstance(body, dict):
            image_name = body.get("imageName") or body.get("image")
    except Exception:
        image_name = None

    if not image_name:
        return _response(400, {"error": "Missing 'imageName' in request body"})

    # Normalize image name by stripping any leading path
    image_name = os.path.basename(image_name)
    key = f"{IMAGES_PREFIX}{image_name}"

    # 1) Check existence (head_object). This avoids generating URLs for missing keys.
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("404", "NoSuchKey", "NotFound"):
            return _response(404, {"error": f"Image not found: {image_name}"})
        return _response(403, {"error": f"Access denied or error checking object: {code}"})

    # 2) Generate the pre-signed URL
    try:
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": BUCKET_NAME, "Key": key},
            ExpiresIn=URL_EXPIRATION_SECONDS,
        )

        # Compute expiration as epoch seconds for frontend countdown
        expires_epoch_seconds = int(time.time()) + URL_EXPIRATION_SECONDS

        return _response(200, {"url": url, "expires": expires_epoch_seconds})

    except Exception as e:
        return _response(500, {"error": f"Failed to generate pre-signed URL: {str(e)}"})

