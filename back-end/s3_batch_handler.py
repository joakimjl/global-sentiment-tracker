import boto3
import boto3.session
from settings import POSTGRES_PASSWORD, POSTGRES_USER, CONNECT_IP_REMOTE, CONNECT_PORT_REMOTE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import os
import zipfile
import datetime

def fix_path(path):
    new_path = ""
    for char in path:
        if char != ":":
            new_path += char
        else:
            new_path += "_"
    path = new_path
    return new_path

class S3BatchHandler():
    def __init__(self, specific_name=None):
        self.batch_name = None
        self.specific_name = specific_name

    def zip_batch(self, dir="temp_articles", added_name="fetched",day=datetime.datetime.now()):
        self.batch_name = added_name+"_batch_"+str(day)+".zip"
        self.batch_name = fix_path(self.batch_name)
        ziper = zipfile.ZipFile(self.batch_name, "w")
        if not os.path.isdir(dir):
            dir = "back-end/"+dir
            if not os.path.isdir(dir):
                raise NameError(f"Dir name '{dir}' not found")
        
        for filename in os.listdir(dir):
            #if filename.endswith(str(day)+" 00_00_00")
            f = os.path.join(dir,filename)
            if os.path.isfile(f):
                ziper.write(f)
        
        ziper.close()
        self._upload_batch()
        print(f"Uploaded: {self.batch_name}")
        for filename in os.listdir(dir):
            #if filename.endswith(str(day)+" 00_00_00")
            f = os.path.join(dir,filename)
            if os.path.isfile(f):
                os.remove(f)
        return True
    
    def unzip_batch(self, dir="temp_articles", added_name="fetched",day=datetime.date.today()):
        if self.specific_name:
            if self.specific_name.endswith(".zip") == False:
                self.specific_name = self.specific_name+".zip"
            self.batch_name = self.specific_name
        else:
            self.batch_name = fix_path(added_name+"_batch_"+str(day)+".zip")
        with zipfile.ZipFile(self.batch_name, 'r') as ziper:
            if not os.path.isdir(dir):
                dir = "back-end/"+dir
                if not os.path.isdir(dir):
                    raise NameError(f"Dir name '{dir}' not found")
            ziper.extractall("")
        return True
            
    def _upload_batch(self):
        s3_client = boto3.client('s3')
        s3_client.upload_file(self.batch_name, "gst-batch-process", self.batch_name)

    def _download_batch(self, path="", zip=False):
        s3_client = boto3.client('s3')
        extension = ""
        if zip == True:
            extension = ".zip"
        self.batch_name = self.batch_name+extension
        if os.path.isfile(self.batch_name):
            return "Done"
        s3_client.download_file("gst-batch-process", self.batch_name, path+self.batch_name)

    def upload_processed(self, path, added_name="processed",day=None):
        """Path needs to be given as string of path+filename"""
        path = fix_path(path)
        self.zip_batch("temp_processed",added_name="processed",day=day)
        print(f"Uploaded {path}")
        return True
    
    def fetch_processed(self, path, added_name="processed",day=datetime.date.today().strftime("%Y-%m-%d"),zip=False):
        if self.specific_name:
            self.batch_name = self.specific_name
        else:
            self.batch_name = fix_path(added_name+"_batch_"+day+".zip")
        added_zip_part = ""
        if zip == True:
            added_zip_part = ".zip"
        if (os.path.isfile(self.batch_name+added_zip_part)):
            self.unzip_batch("temp_processed",added_name=added_name,day=day)
            return True
        if self._download_batch(zip=zip) == "Done":
            return
        self.unzip_batch("temp_processed",added_name=added_name,day=day)
        if not os.path.isfile(path):
            return False
        
        print(f"Downloaded {path}")
        return True

if __name__ == "__main__":
    handler = S3BatchHandler(specific_name = "fetched_batch_2025-01-20 04_14_07.461557.zip")
    handler.fetch_processed("temp_processed",added_name="processed")
