from enum import Enum
from typing import List, Optional

import requests
from pydantic import BaseModel

ANSWERS_PATH = "answers"
QUESTION_KEY = "question"
HEADER_ACCEPT_LANGUAGE_KEY = "Accept-Language"
DEFAULT_LANGUAGE = "en-US"
HTTP_OK = 200


class QuestionAnsweringStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class QuestionAnsweringResponse(BaseModel):
    answers: Optional[List[str]]
    status: QuestionAnsweringStatus


class QuestionAnsweringProtocol:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_response(
        self, question: str, language: str = DEFAULT_LANGUAGE
    ) -> QuestionAnsweringResponse:
        response = requests.get(
            f"{self.base_url}/{ANSWERS_PATH}",
            params={QUESTION_KEY: question},
            headers={HEADER_ACCEPT_LANGUAGE_KEY: language},
        )

        return (
            QuestionAnsweringResponse(
                **response.json(), status=QuestionAnsweringStatus.SUCCESS
            )
            if response.status_code == HTTP_OK
            else QuestionAnsweringResponse(status=QuestionAnsweringStatus.FAILURE)
        )
