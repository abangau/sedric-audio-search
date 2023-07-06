from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from models.sentence import Sentence


class TranscriptStatus(Enum):
    """Represents the possible states of transcript analysis requests.
    """
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

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
    created: datetime
    updated: datetime
    file_type: FileType
    sentences: List[Sentence]
    transcript_path: str = None
    status: str = TranscriptStatus.PENDING

    def __post_init__(self) -> None:
        """Deserializes into transcript object with Python data types.
        """
        self.created = datetime.fromisoformat(self.created) if isinstance(self.created, str) else self.created
        self.updated = datetime.fromisoformat(self.updated) if isinstance(self.updated, str) else self.updated
        self.request_id = UUID(self.request_id) if isinstance(self.request_id, str) else self.request_id
        self.file_type = FileType(self.file_type) if isinstance(self.file_type, str) else self.file_type
        self.status = TranscriptStatus(self.status) if isinstance(self.status, str) else self.status
        self.sentences = [
            Sentence(**s) if not isinstance(s, Sentence) else s
            for s in self.sentences
        ]

    def as_dict(self) -> dict:
        """Encodes the transcript to a python dictionary so it can be sent as json to dynamo.

        :return: Transcript as python dictionary with standard json fields.
        :rtype: dict
        """
        return {
            "request_id": self.request_id.hex,
            "audio_url": self.audio_url,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "file_type": self.file_type.value,
            "status": self.status.value,
            "sentences": [s.as_dict() for s in self.sentences],
            "transcript_path": self.transcript_path
        }

    @property
    def audio_file_path(self):
        return f'audio/{self.request_id.hex}/audio_file.{self.file_type.value}'

    @property
    def transcript_file_path(self):
        return f'transcripts/{self.request_id.hex}/transcript.json'

    @property
    def results_file_path(self):
        return f'results/{self.request_id.hex}/results.json'
