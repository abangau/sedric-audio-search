import boto3

from models.transcript import Transcript


class TranscribeService(object):

    def __init__(self) -> None:
        self.transcribe_client = boto3.client('transcribe')

    def start_transcribe_job(
            self,
            transcript: Transcript,
            input_bucket: str,
            output_bucket: str) -> str:
        """Starts the aws transcribe job for the given transcript.

        :param transcript: The metadata object with the necessary paths.
        :type transcript: Transcript
        :param input_bucket: The bucket where the audio file can be found.
        :type input_bucket: str
        :param output_bucket: The bucket where transcribe should save the generated transcript.
        :type output_bucket: str
        :return: The transcription job's id returned by transcribe.
        :rtype: str
        """
        job_args = {
            'TranscriptionJobName': transcript.request_id.hex,
            'Media': {'MediaFileUri': f's3://{input_bucket}/{transcript.audio_file_path}'},
            'MediaFormat': transcript.file_type.value,
            'OutputKey': transcript.transcript_file_path,
            'OutputBucketName': output_bucket,
            'LanguageCode': 'en-US'
        }
        response = self.transcribe_client.start_transcription_job(**job_args)
        return response['TranscriptionJob']
