from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4

from models.sentence import Sentence


class TranscriptStatus(Enum):
    """Represents the possible states of transcript analysis requests.
    """
    PENDING = 1
    FINISHED = 2
    FAILED = 3

class FileType(Enum):
    """Accepted file types
    """
    WAV = 'wav'
    MP3 = 'mp3'


@dataclass
class Transcript:
    """Dataclass representing all metadata associated with a transcript process request.
    """
    request_id: uuid4
    audio_url: str
    file_type = FileType
    sentences: List(Sentence)
    status: int = TranscriptStatus.PENDING
    created: datetime
    updated: datetime

    @property
    def audio_file_path(self):
        return f'audio/{self.request_id.hex}/audio_file.{self.file_type.value}'

    @property
    def transcript_file_path(self):
        return f'transcripts/{self.request_id.hex}/transcript.json'

    @property
    def results_file_path(self):
        return f'results/{self.request_id.hex}/results.json'
