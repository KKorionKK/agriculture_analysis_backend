from api.common.handler import BaseHandler
import io

from api.services.uploader import MediaUploader


class UploadHandler(BaseHandler):
    media_uploader = MediaUploader()

    async def post(self):
        data = self.request.files["data"][0]
        filename: str = data["filename"]
        body = data["body"]

        buffer = io.BytesIO(body)

        url = await self.media_uploader.upload_data(buffer, filename.split(".")[-1])

        self.write({"url": url})
