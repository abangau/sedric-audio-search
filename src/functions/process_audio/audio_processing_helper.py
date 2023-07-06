from common.models.transcript import Transcript, TranscriptStatus
from common.services.s3_service import S3Service
from common.services.transcribe_service import TranscribeService
from common.services.transcript_storage_service import TranscriptStorageService


class AudioProcessingHelper(object):

    def __init__(self, ddb_table, s3_bucket):
        self.transcripts_service = TranscriptStorageService(ddb_table=ddb_table)
        self.s3_service = S3Service()
        self.transcribe_service = TranscribeService()
        self.s3_bucket = s3_bucket


    def get_transcript_metadata(self, request_id: str) -> Transcript:
        """Gets the transcript record from ddb.

        :param request_id: The id of the request (used to uniquely identify transcripts)
        :type request_id: str
        :return: The transcript object
        :rtype: Transcript
        """
        return self.transcripts_service.get_transcript(request_id)

    def transfer_audio_file(self, transcript: Transcript) -> str:
        """Copies the file from the given url into our bucket for processing with transcribe.

        :param transcript: The transcript object containing metadata about the request.
        :type transcript: Transcript
        :return: The path of the audio file
        :rtype: str
        """
        self.s3_service.copy_audio_file_from_url(
            url=transcript.audio_url,
            bucket=self.s3_bucket,
            s3_key=transcript.audio_file_path
        )

        return transcript.audio_file_path

    def start_transcribe_task(self, transcript: Transcript) -> str:
        """Will perform an audio transcription using aws Transcribe.

        :param transcript: The metadata object containing the transcription request.
        :type transcript: Transcript
        :return: The id used to determine the status of the transcribe job.
        :rtype: str
        """
        # We're only using one bucket.
        self.transcribe_service.start_transcribe_job(transcript, self.s3_bucket, self.s3_bucket)

    def set_transcript_request_failed(self, transcript: Transcript) -> None:
        """Will mark the status of the transcript as failed and save to dynamodb.

        :param transcript: The transcript that failed to process the audio file.
        :type transcript: Transcript
        """
        transcript.status = TranscriptStatus.FAILED
        self.transcripts_service.put_transcript(transcript)
