from dotenv import load_dotenv

import os

from utilities.cos_client import QCloudCosClient


class BlobClient:
    def __init__(self):
        load_dotenv()

        self.blobType = os.getenv('BLOB_STORE_TYPE')
        if self.blobType == 'COS':
            self.cosClient = QCloudCosClient()

    def upload_file(self, bytes_data, file_name):
        if self.blobType == 'COS':
            return self.cosClient.put_object(bytes_data, file_name)

        return file_name

    def delete_file(self, file_name):
        if self.blobType == 'COS':
            self.cosClient.delete_object(file_name)

    def get_all_files(self, k: int = None):
        if self.blobType == 'COS':
            return self.cosClient.list_objects(k)

        return []

