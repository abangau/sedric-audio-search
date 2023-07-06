from aws_lambda_powertools.utilities.parser import Field, BaseModel


class CheckSentencesRequest(BaseModel):
    """The schema of the event body.
    """
    audio_url: str = Field(..., min_length=10, max_length=128),
    sentences: list[str] = Field(..., min_length=1, max_length=256)
