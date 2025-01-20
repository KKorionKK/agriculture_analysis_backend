import boto3

from uuid import uuid4
from io import BytesIO


S3_ACCESS_ID = "C26MAFLVNUMGK8RFV5SS"
S3_SECRET_KEY = "DshkL9P6lYUGALHmcyDstsNlLBEO3etRqKFuzLzC"
S3_BUCKET = "058ec85b-a033d29f-40af-47a8-b537-af7433b01be1"


class MediaUploader:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url="https://s3.timeweb.cloud",
            region_name="ru-1",
            aws_access_key_id=S3_ACCESS_ID,
            aws_secret_access_key=S3_SECRET_KEY,
        )

    async def upload_data(self, media: BytesIO, extension: str) -> str:
        media.seek(0)
        s3_key = uuid4().hex + "." + extension
        self.s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=media)
        return f"https://s3.timeweb.cloud/{S3_BUCKET}/{s3_key}"
