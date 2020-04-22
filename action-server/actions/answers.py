import logging
from enum import Enum
from typing import List, Optional

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


ANSWERS_PATH = "answers"
QUESTION_KEY = "question"
HEADER_ACCEPT_LANGUAGE_KEY = "Accept-Language"
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

    def get_response(self, question: str, language: str) -> QuestionAnsweringResponse:
        url = f"{self.base_url}/{ANSWERS_PATH}"
        params = {QUESTION_KEY: question}
        headers = {HEADER_ACCEPT_LANGUAGE_KEY: language}

        logger.info(
            "Performing question answering request: url=%s params=%s, headers=%s",
            url,
            params,
            headers,
        )

        response = requests.get(url, params=params, headers=headers)

        logger.info("Got question answering response: %s", response.text)

        return (
            QuestionAnsweringResponse(
                **response.json(), status=QuestionAnsweringStatus.SUCCESS
            )
            if response.status_code == HTTP_OK
            else QuestionAnsweringResponse(status=QuestionAnsweringStatus.FAILURE)
        )
