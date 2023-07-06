import json
import boto3


class SQSService(object):
    def __init__(self):
        self.sqs = boto3.client('sqs')

    def send_message(self, message: dict, queue_url: str):
        """Sends a message (as encoded json) to the given sqs queue.

        :param message: The message to send.
        :type message: dict
        :param queue_url: The URL of the queue to use.
        :type queue_url: str
        """
        return self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
