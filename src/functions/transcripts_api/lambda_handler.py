import os
from urllib.parse import urlparse

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from analysis_helper import AnalysisHelper
from validation.request_models import CheckSentencesRequest

logger: Logger = Logger(service='transcripts_api')
app: APIGatewayRestResolver = APIGatewayRestResolver()

@app.post('/submit_request')
def post_submit_request() -> dict[str, any]:
    """Handler for submitting new audio files and sentences request.

    :return: Response which contains a request_id to follow up on processing status.
    :rtype: dict
    """
    request_data: CheckSentencesRequest = CheckSentencesRequest(**app.current_event.json_body)
    path = urlparse(request_data.audio_url).path
    ext = os.path.splitext(path)[1]
    if ext not in ['.wav', '.mp3']:
        return {
            'body': {
                'message': 'Error! Only mp3 or wav files are supported.'
            },
            'status_code': 400
        }
    helper: AnalysisHelper = AnalysisHelper()
    logger.info('Creating new transcript analysis request.')
    request_id: str = helper.save_transcript_analysis_request(request_data.audio_url, request_data.sentences, ext)
    logger.info('Successfully created new analysis request, scheduling processing task.')
    helper.register_transcribe_task(request_id)
    logger.info('Successfully registered transcribe task.')

    return {
        'body': {
            'request_id': request_id,
            'message': 'Your request was accepted successfully'
        }
    }

@app.get('/get_results')
def get_results_request() -> dict[str, any]:
    """TODO: Implement the get_results route

    :return: _description_
    :rtype: dict[str, any]
    """
    pass

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: dict[str, any], context: LambdaContext) -> dict[str, any]:
    return app.resolve(event, context)
