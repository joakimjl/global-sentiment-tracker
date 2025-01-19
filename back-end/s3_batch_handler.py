import boto3
import boto3.session
from settings import POSTGRES_PASSWORD, POSTGRES_USER, CONNECT_IP_REMOTE, CONNECT_PORT_REMOTE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import os
import zipfile
import datetime

class S3BatchHandler():
    def __init__(self):
        self.batch_name = None

    def zip_batch(self):
        self.batch_name = "batch_"+str(datetime.datetime.now())+".zip"
        ziper = zipfile.ZipFile(self.batch_name, "w")
        dir = "temp_articles"
        if not os.path.isdir(dir):
            dir = "back-end/temp_articles"
            if not os.path.isdir(dir):
                raise NameError("Dir name not found")
        
        for filename in os.listdir(dir):
            f = os.path.join(dir,filename)
            if os.path.isfile(f):
                ziper.write(f)
        
        ziper.close()
        self._upload_batch()
        return True
            
    def _upload_batch(self):
        s3_client = boto3.client('s3')
        s3_client.upload_file(self.batch_name, "gst-batch-process", self.batch_name)

    def upload_processed(self, path):
        """Path needs to be given as string of path+filename"""
        if not os.path.isfile(path):
            return False
        self.batch_name = path
        self._upload_batch()
        print(f"Uploaded {path}")
        return True

if __name__ == "__main__":
    handler = S3BatchHandler()
    handler.zip_batch()