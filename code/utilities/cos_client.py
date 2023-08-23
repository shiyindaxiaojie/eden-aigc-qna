from datetime import datetime

import pytz
from dotenv import load_dotenv

import os

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

tz = pytz.timezone('Asia/Shanghai')

# 腾讯云对象存储
class QCloudCosClient:
    def __init__(self):
        load_dotenv()
        self.region: str = os.getenv("QCLOUD_COS_REGION")
        self.secret_id: str = os.getenv("QCLOUD_COS_SECRET_ID")
        self.secret_key: str = os.getenv("QCLOUD_COS_SECRET_KEY")
        self.token: str = os.getenv("QCLOUD_COS_TOKEN")
        self.bucket: str = os.getenv("QCLOUD_COS_BUCKET")

        config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key, Token=self.token)
        self.client = CosS3Client(config)

    def put_object(self, body, key):
        response = self.client.put_object(
            Bucket=self.bucket,
            Body=body,
            Key=key,
            EnableMD5=False
        )
        return self.client.get_object_url(Bucket=self.bucket, Key=key)

    def delete_object(self, key):
        response = self.client.delete_object(
            Bucket=self.bucket,
            Key=key
        )
        return response

    def list_objects(self, k: int = 10):
        response = self.client.list_objects(Bucket=self.bucket, Prefix="", MaxKeys=10)
        files = []
        if "Contents" in response:
            for content in response["Contents"]:
                files.append({
                    "filename": content["Key"],
                    "size": "{:.2f} KB".format(float(content["Size"])/1024),
                    "last_modified": datetime.strptime(content["LastModified"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
                    })
        return files
