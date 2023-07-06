from dataclasses import dataclass

@dataclass
class Sentence:
    """Dataclass representing a sentence which was searched for in the transcript.
    """
    plain_text: str
    was_present: bool = False
    start_word_index: int = None
    end_word_index: int = None

    def as_dict(self) -> dict:
        """Returns the sentence encoded as a standard python dictionary

        :rtype: dict
        """
        return {
            "plain_text": self.plain_text,
            "was_present": self.was_present,
            "start_word_index": self.start_word_index,
            "end_word_index": self.end_word_index
        }
