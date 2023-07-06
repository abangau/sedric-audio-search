import os

from models.transcript import Transcript, TranscriptStatus
from services.s3_service import S3Service
from services.transcript_storage_service import TranscriptStorageService


class AnalyseTrascriptHelper(object):

    def __init__(self):
        self.s3_bucket = os.environ['TRANSCRIPTS_BUCKET']
        self.transcript_storage_service: TranscriptStorageService = TranscriptStorageService(
            os.environ['TRANSCRIPTS_TABLE']
        )
        self.s3_service = S3Service()

    def get_transcript_results(self, obj_key: str) -> dict:
        """Gets the results from s3

        :param obj_key: The key of the transcribe results.
        :type obj_key: str
        :return: Results as a dict
        :rtype: dict
        """
        return self.s3_service.read_json_file(bucket=self.s3_bucket, s3_key=obj_key)

    def get_transcript_metadata(self, request_id: str) -> Transcript:
        """Loads transcript metadata model from dynamo db.

        :param request_id: The request id for the transcript analysis request.
        :type request_id: str
        :return: The metadata object.
        :rtype: Transcript
        """
        return self.transcript_storage_service.get_transcript(request_id)

    def analyse_transcript(self, transcript_data: dict, transcript_metadata: Transcript) -> Transcript:
        """Performs the search on the transcript's items (words) for the requested sentences.

        :param transcript_data: The transcript returned from Transcribe.
        :type transcript_data: dict
        :param transcript_metadata: The metadata of the search request.
        :type transcript_metadata: Transcript
        :return: Transcript with matches updated.
        :rtype: Transcript
        """
        transcript_items = transcript_data.get('results', {}).get('items', [])
        words_found_counters = [0] * len(transcript_metadata.sentences)

        # So we don't have to do this transformation on every iteration,
        # let's generate lists of words for each sentence
        sentence_words = [sentence.plain_text.split(' ') for sentence in transcript_metadata.sentences]

        # This could be done more elegantly with something like elasticsearch/opensearch
        # But this implementation should work fine for the demo, and not be very slow as it will only iterate
        # over all the words of the transcript once and find all matching sentences while doing so.
        for idx, item in enumerate(transcript_items):
            # Only use the first alternative as it's highest confidence
            word_in_transcript = item['alternatives'][0]['content']
            for sentence_idx, _ in enumerate(transcript_metadata.sentences):
                current_sentence_counter = words_found_counters[sentence_idx]
                # Case insensitive match
                if sentence_words[sentence_idx][current_sentence_counter].lower() == word_in_transcript.lower():
                    # We found a correct word, increase counter to find the next
                    words_found_counters[sentence_idx] += 1

                if len(sentence_words[sentence_idx]) == words_found_counters[sentence_idx]:
                    # We found all the words that are in the sentence, we need to set the sentence as found
                    # Also add the indices
                    transcript_metadata.sentences[sentence_idx].was_present = True
                    transcript_metadata.sentences[sentence_idx].start_word_index = idx - len(sentence_words[sentence_idx])
                    transcript_metadata.sentences[sentence_idx].end_word_index = idx

                    # This is to reset the words found counter for the index.
                    # This means it will only find the last occurrence
                    words_found_counters[sentence_idx] = 0

        return transcript_metadata

    def save_analysis_results(self, transcript_metadata: Transcript, transcript_path: str) -> None:
        """Saves the transcript, also saves the status and the transcripts result path.

        :param transcript_metadata: _description_
        :type transcript_metadata: Transcript
        :param transcript_path: _description_
        :type transcript_path: str
        """
        transcript_metadata.status = TranscriptStatus.COMPLETED
        transcript_metadata.transcript_path = transcript_path
        self.transcript_storage_service.put_transcript(transcript_metadata)
