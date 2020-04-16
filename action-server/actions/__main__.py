import os
import sys

from actions.answers import QuestionAnsweringProtocol, QuestionAnsweringResponse

FAQ_URL_ENV_KEY = "COVID_FAQ_SERVICE_URL"
DEFAULT_FAQ_URL = "https://covidfaq.dialoguecorp.com"


def main(question: str):
    protocol = QuestionAnsweringProtocol(
        os.environ.get(FAQ_URL_ENV_KEY, DEFAULT_FAQ_URL)
    )
    response: QuestionAnsweringResponse = protocol.get_response(question)
    print(response.answers)
    print(response.status)


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        main(args[1])
    else:
        print("Usage: __main__.py 'QUESTION' to test Q&A web requests.")
