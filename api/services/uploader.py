import boto3

from uuid import uuid4
from io import BytesIO
from api import config


class MediaUploader:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url="https://s3.timeweb.cloud",
            region_name="ru-1",
            aws_access_key_id=config.S3_ACCESS_ID,
            aws_secret_access_key=config.S3_SECRET_KEY,
        )

    async def upload_data(self, media: BytesIO, extension: str) -> str:
        media.seek(0)
        s3_key = uuid4().hex + "." + extension
        self.s3.put_object(Bucket=config.S3_BUCKET, Key=s3_key, Body=media)
        return f"https://s3.timeweb.cloud/{config.S3_BUCKET}/{s3_key}"
