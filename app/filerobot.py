import os
import json

import requests

from app.constants import FILEROBOT_API_ENDPOINT, APIS_TIMEOUT


class Filerobot:
    def __init__(self, filerobot_token, filerobot_key):
        self.filerobot_token = filerobot_token
        self.filerobot_key = filerobot_key

    def upload_endpoint(self, folder=None):
        filerobot_upload_dir = os.environ.get("FILEROBOT_DIR")
        endpoint = f"{FILEROBOT_API_ENDPOINT}/{self.filerobot_token}/v4/upload?dir={filerobot_upload_dir}"
        if folder is not None:
            if not folder.startswith("/"):
                folder = f"/{folder}"
            endpoint = f"{endpoint}{folder}"
        return endpoint

    @property
    def update_endpoint(self):
        # TODO: Fix the update methods
        return f"{FILEROBOT_API_ENDPOINT}/{self.filerobot_token}/v4/upload"

    def _perform_post_upload_urls(self, post_data):
        post_headers = {
            "Content-Type": "application/json",
            "X-Airstore-Key": self.filerobot_key
        }
        response = requests.post(url=self.upload_endpoint(), data=json.dumps(post_data), headers=post_headers, timeout=APIS_TIMEOUT)
        print(response.content)
        try:
            result_json = json.loads(response.content.decode('utf8'))
            return response, result_json
        except:
            print(f"ERROR PARSING response {response.content} - LOAD: {post_data}")
            return response, {}

    def _perform_post_upload(self, files, folder=None):
        post_headers = {
            "X-Airstore-Key": self.filerobot_key
        }

        response = requests.post(url=self.upload_endpoint(folder), files=files, headers=post_headers, timeout=APIS_TIMEOUT)
        result_json = json.loads(response.content.decode('utf8'))
        return response, result_json

    def multipart_upload(self, file_list, folder):
        files_to_upload = {}
        for i, file in enumerate(file_list):
            files_to_upload[f"file_{i}"] = open(file, "rb")
        return self._perform_post_upload(files=files_to_upload, folder=folder)

    def urls_upload(self, urls_list):
        end_list = []

        for url in urls_list:
            try:
                el = {"url": url, "info": {"origin": url}}
                end_list.append(el)
            except:
                continue

        post_data = {
            "files_urls": end_list
        }
        return self._perform_post_upload_urls(post_data=post_data)
