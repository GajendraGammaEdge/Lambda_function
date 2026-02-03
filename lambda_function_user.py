import json
import boto3
import os
from PIL import Image
from io import BytesIO
import urllib.parse

s3 = boto3.client("s3")
COMPRESS_QUALITY = 60

def lambda_handler(event, context):
    DEST_BUCKET = os.environ["DEST_BUCKET"]

    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        object_key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        if source_bucket == DEST_BUCKET:
            print("Skipping destination bucket to avoid loop")
            continue

        if not object_key.lower().endswith((".jpg", ".jpeg", ".png")):
            print(f"Skipping non-image: {object_key}")
            continue

        response = s3.get_object(
            Bucket=source_bucket,
            Key=object_key
        )
        image_content = response["Body"].read()

        img = Image.open(BytesIO(image_content)).convert("RGB")

        buffer = BytesIO()
        img.save(
            buffer,
            format="JPEG",
            quality=COMPRESS_QUALITY,
            optimize=True
        )
        buffer.seek(0)

        dest_key = f"compressed/{object_key}"

        s3.put_object(
            Bucket=DEST_BUCKET,
            Key=dest_key,
            Body=buffer,
            ContentType="image/jpeg"
        )

        print(f"Compressed and uploaded: {dest_key}")

    return {
        "statusCode": 200,
        "body": "Images processed successfully"
    }
