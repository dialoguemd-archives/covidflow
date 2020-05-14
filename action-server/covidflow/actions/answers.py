import re
from enum import Enum
from typing import List, Optional

import structlog
from aiohttp import ClientSession
from pydantic import BaseModel

logger = structlog.get_logger()


ANSWERS_PATH = "answers"
QUESTION_KEY = "question"
RESPONSE_ANSWERS_KEY = "answers"
HEADER_ACCEPT_LANGUAGE_KEY = "Accept-Language"
HTTP_OK = 200

REGEX_HTML_TAG = re.compile("<.*?>")


class QuestionAnsweringStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEED_ASSESSMENT = "need_assessment"
    OUT_OF_DISTRIBUTION = "out_of_distribution"


class QuestionAnsweringResponse(BaseModel):
    answers: Optional[List[str]]
    status: QuestionAnsweringStatus


class QuestionAnsweringProtocol:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_response(
        self, session: ClientSession, question: str, language: str
    ) -> QuestionAnsweringResponse:
        url = f"{self.base_url}/{ANSWERS_PATH}"
        params = {QUESTION_KEY: question}
        headers = {HEADER_ACCEPT_LANGUAGE_KEY: language}

        logger.info(
            "Performing question answering request: url=%s params=%s, headers=%s",
            url,
            params,
            headers,
        )
        async with session.get(url, params=params, headers=headers) as response:
            json_dict = await response.json()
            logger.info("Got question answering response: %s", response)
            if response.status == HTTP_OK:
                return QuestionAnsweringResponse(
                    answers=format_answers(json_dict.get(RESPONSE_ANSWERS_KEY, None)),
                    status=QuestionAnsweringStatus.SUCCESS
                    if json_dict.get(RESPONSE_ANSWERS_KEY, None)
                    else QuestionAnsweringStatus.OUT_OF_DISTRIBUTION,
                )
            else:
                return QuestionAnsweringResponse(status=QuestionAnsweringStatus.FAILURE)


def format_answers(answers: Optional[List[str]]) -> Optional[List[str]]:
    return (
        [re.sub(REGEX_HTML_TAG, "", answer) for answer in answers] if answers else None
    )
