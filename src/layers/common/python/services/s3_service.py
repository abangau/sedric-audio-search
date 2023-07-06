import boto3

from datetime import datetime, timedelta
import json
import urllib3

class S3Service(object):
    def __init__(self):
        self.client = boto3.client('s3')
        self.http = urllib3.PoolManager()

    def copy_audio_file_from_url(self, url: str, bucket: str, s3_key: str):
        """Will download (stream) the file from the given URL into the specified s3 location.

        :param url: The URL of the audio file
        :type url: str
        :param bucket: The s3 bucket to save to
        :type bucket: str
        :param s3_key: The key under which to place the object
        :type s3_key: str
        """
        self.client.upload_fileobj(
            self.http.request(
                'GET',
                url,
                preload_content=False
            ),
            bucket,
            s3_key
        )

    def create_presigned_url(self, bucket: str, s3_key: str) -> dict:
        """Creates a presigned url for the given key. Expires in 15 minutes.

        :param bucket: The bucket to create the presigned url for.
        :type bucket: str
        :param s3_key: The key of the object to generate the rul for.
        :type s3_key: str
        :return: A dict with two keys: url and expires_at
        :rtype: dict
        """
        return self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': s3_key
            },
            ExpiresIn=15 * 60
        )

    def read_json_file(self, bucket: str, s3_key: str) -> dict:
        """Generic function for reading a json file and returning a python dictionary.

        :param bucket: Bucket where file is located
        :type bucket: str
        :param s3_key: The key of the json file to read
        :type s3_key: str
        :return: The parsed json file as a python dict.
        :rtype: dict
        """
        obj = self.client.get_object(Bucket=bucket, Key=s3_key).get('Body')
        if obj:
            return json.loads(obj.read().decode('utf-8'))

        raise Exception(f'Failed to read file: {bucket}/{s3_key}')
