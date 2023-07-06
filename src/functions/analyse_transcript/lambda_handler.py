from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext

from analyse_transcript_helper import AnalyseTrascriptHelper

logger: Logger = Logger(service='analyse_transcript')


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, ctx: LambdaContext):
    event_obj = S3Event(event)
    helper = AnalyseTrascriptHelper()
    for record in event_obj.records:
        # Path of the transcript
        transcript_path: str = record.s3.get_object.key
        # Extract request_id from transcript path
        request_id = transcript_path.split('/')[1]
        print(request_id)
        # Load transcript and metadata
        logger.info(f'Loading transcript for request_id: {request_id}')
        transcript = helper.get_transcript_results(transcript_path)
        transcript_metadata = helper.get_transcript_metadata(request_id=request_id)

        # Find sentences
        logger.info(f'Processing for request_id: {request_id}')
        solved_transcript_metadata = helper.analyse_transcript(transcript, transcript_metadata)

        # Save results
        logger.info(f'Saving results for request_id: {request_id}')
        helper.save_analysis_results(solved_transcript_metadata, transcript_path)
