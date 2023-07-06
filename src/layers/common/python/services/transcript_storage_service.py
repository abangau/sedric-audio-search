from models.transcript import Transcript
from services.providers.dynamodb_provider import DynamoDBProvider


class TranscriptStorageService(object):
    """Helpers class to store/load transcripts from DynamoDB
    """

    def __init__(self, ddb_table: str):
        """Will create a new connection to DDB in order to store/retrieve transcripts.

        :param ddb_table: The name of the dynamo table to use.
        :type ddb_table: str
        """
        self.dynamo_client = DynamoDBProvider.get_instance(ddb_table)

    def put_transcript(self, transcript: Transcript) -> bool:
        """
        Updates dynamodb representation of the model
        """
        self.dynamo_client.table.put_item(Item=transcript.as_dict())

    def get_transcript(self, request_id: str) -> Transcript:
        """Will retrieve a transcript from dynamodb.

        :param request_id: The request id of the transcript submission.
        :type request_id: str
        :return: The transcript for the given request_id
        :rtype: Transcript
        """
        item: dict = self.dynamo_client.table.get_item(
            Key={
                'request_id': request_id
            }
        )['Item']
        return Transcript(**item)
