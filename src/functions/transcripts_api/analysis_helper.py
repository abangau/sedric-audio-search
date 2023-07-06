import datetime
import os
from uuid import uuid4

from models.sentence import Sentence
from models.transcript import Transcript, FileType
from services.s3_service import S3Service
from services.sqs_service import SQSService
from services.transcript_storage_service import TranscriptStorageService


class AnalysisHelper(object):
    """Helper class for storing analysis requests and registering transcribe tasks on the queue.
    """

    def __init__(self):
        self.transcript_storage_service: TranscriptStorageService = TranscriptStorageService(os.environ['TRANSCRIPTS_TABLE'])
        self.sqs_service: SQSService = SQSService()
        self.audio_process_queue: str = os.environ.get('AUDIO_TRANSCRIBE_QUEUE_URL')
        self.s3_service: S3Service = S3Service()

    def get_transcript_metadata(self, request_id: str) -> Transcript:
        """Fetches transcript metadata from dynamo.

        :param request_id: The request id for the metadata to fetch.
        :type request_id: str
        :return: The metadata.
        :rtype: Transcript
        """
        return self.transcript_storage_service.get_transcript(request_id)

    def save_transcript_analysis_request(self, file_url: str, sentences: list[str], extension: str) -> str:
        """Generates a new Transcript object and stores it.

        :param file_url: The URL path for the wav/mp3.
        :type file_url: str
        :param sentences: A list of sentences to be used for searching the transcript.
        :type sentences: List
        :param extension: The extension of the file.
        :type extension: str
        :return: The request_id used to get status and results.
        :rtype: str
        """
        transcript: Transcript = Transcript(
            request_id=uuid4(),
            audio_url=file_url,
            sentences=[
                Sentence(
                    plain_text=text
                ) for text in sentences
            ],
            file_type=FileType(extension[1:]),
            created=datetime.datetime.now(),
            updated=datetime.datetime.now()
        )
        self.transcript_storage_service.put_transcript(transcript)
        return transcript.request_id.hex

    def register_transcribe_task(self, req_id: str) -> None:
        """Will post a sqs message on the transcribe_audio_file queue.

        :param req_id: The request id used to identify the request
        :type req_id: str
        """
        self.sqs_service.send_message(
            {
                'request_id': req_id
            },
            self.audio_process_queue
        )

    def generate_presigned_url(self, transcript_path: str) -> str:
        """Generates a presigned url to access the transcript on s3.

        :param transcript_path: The path to the transcript on s3.
        :type transcript_path: str
        :return: The url that can be used to get the transcript results.
        :rtype: str
        """
        return self.s3_service.create_presigned_url(os.environ.get('TRANSCRIPTS_BUCKET'), transcript_path)
