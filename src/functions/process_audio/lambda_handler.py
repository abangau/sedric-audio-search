import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from audio_processing_helper import AudioProcessingHelper

from models.transcript import Transcript
from services.transcript_storage_service import TranscriptStorageService

logger: Logger = Logger(service='process_audio')


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    event_obj = SQSEvent(event)
    file_processing_helper = AudioProcessingHelper(os.environ.get('TRANSCRIPTS_TABLE'), os.environ.get('TRANSCRIPTS_BUCKET'))
    for record in event_obj.records:
        # This lambda could process multiple files at once.
        request_id = record.json_body.get('request_id')

        if not request_id:
            logger.warning('Received event without a request_id!')
            continue

        logger.info(f'Getting transcript info for {request_id}!')
        transcript: Transcript = file_processing_helper.get_transcript_metadata(request_id=request_id)

        try:
            logger.info('Transfering audio file!')
            file_processing_helper.transfer_audio_file(transcript)
            logger.info('Audio file transfer complete! Starting transcribe job.')
            file_processing_helper.start_transcribe_task(transcript)
            logger.info(f'Successfully transcribe job for {transcript.request_id}')
        except Exception as exc:
            logger.error(f'Failed to process audio file for request: {request_id}! Details: {str(exc)}')
            file_processing_helper.set_transcript_request_failed(transcript)
