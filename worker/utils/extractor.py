import zipfile
import os
import shutil
import requests


class Extractor:
    def __init__(self, current_directory: str = None):
        if current_directory:
            self.default_path = current_directory + "/zips"
        else:
            self.default_path = os.getcwd() + "/zips"
        if not os.path.exists(self.default_path):
            os.mkdir(self.default_path)

    def download(self, href: str, current_hash: str):
        response = requests.get(href)
        with open(f"{self.default_path}/{current_hash}.zip", "wb") as f:
            f.write(response.content)
        return f"{self.default_path}/{current_hash}.zip"

    def extract(self, path: str, current_hash: str):
        extract_dir = self.default_path + f"/{current_hash}"
        os.mkdir(extract_dir)

        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        return extract_dir

    def delete_dir(self, path: str):
        shutil.rmtree(path)
