import os
from pathlib import Path
import boto3
import requests

from uuid import uuid4
from io import BytesIO

S3_ACCESS_ID = "C26MAFLVNUMGK8RFV5SS"
S3_SECRET_KEY = "DshkL9P6lYUGALHmcyDstsNlLBEO3etRqKFuzLzC"
S3_BUCKET = "058ec85b-a033d29f-40af-47a8-b537-af7433b01be1"


class MediaController:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url="https://s3.timeweb.cloud",
            region_name="ru-1",
            aws_access_key_id=S3_ACCESS_ID,
            aws_secret_access_key=S3_SECRET_KEY,
        )
        self.default_folder = Path(os.getcwd(), "/raw/")

    def download(self, links: list[str]) -> list[str]:
        ready: list[str] = []
        for link in links:
            extension = link.split(".")[-1]
            response = requests.get(link)
            img = response.content
            filename = f"{uuid4().hex}.{extension}"
            with open(filename, "w") as f:
                f.write(img)
            ready.append(Path(self.default_folder, filename))

    def upload(self, media: BytesIO, extension: str, prefix: str | None = None) -> str:
        media.seek(0)
        if prefix:
            s3_key = prefix + "." + extension
        else:
            s3_key = uuid4().hex + "." + extension
        self.s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=media)
        return f"https://s3.timeweb.cloud/{S3_BUCKET}/{s3_key}"
