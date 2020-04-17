FROM rasa/rasa:1.9.4
EXPOSE 8080

COPY requirements.txt requirements.txt
COPY actions actions

USER root
RUN pip install -r requirements.txt
USER 1001

CMD [ "run", "actions", "--port", "8080" ]
