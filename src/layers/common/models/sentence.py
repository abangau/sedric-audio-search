from dataclasses import dataclass

@dataclass
class Sentence:
    """Dataclass representing a sentence which was searched for in the transcript.
    """
    plain_text: str
    was_present: bool = False
    start_word_index: int = None
    end_word_index: int = None
