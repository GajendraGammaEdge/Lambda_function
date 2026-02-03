import os
from io import BytesIO
from botocore.stub import Stubber, ANY
from lambda_function_user import lambda_handler, s3

os.environ["DEST_BUCKET"] = "compressed-images-bucket"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "resources", "image.png")

event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "aws-sour-78"},
                "object": {"key": "image_data/download.jpeg"}
            }
        }
    ]
}

with open(IMAGE_PATH, "rb") as f:
    real_image_bytes = f.read()

with Stubber(s3) as stubber:
    stubber.add_response(
        "get_object",
        {
            "Body": BytesIO(real_image_bytes)
        },
        {
            "Bucket": "aws-sour-78",
            "Key": "image_data/download.jpeg"
        }
    )

    stubber.add_response(
        "put_object",
        {},
        {
            "Bucket": "compressed-images-bucket",
            "Key": "compressed/image_data/download.jpeg",
            "Body": ANY,
            "ContentType": "image/jpeg"
        }
    )


    response = lambda_handler(event, None)
    print(response)
