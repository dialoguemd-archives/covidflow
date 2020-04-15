FROM rasa/rasa:1.9.4-full
EXPOSE 8080

ENV ACTION_SERVER_ENDPOINT=http://actions:8080/webhook
ENV TRACKER_STORE_ENDPOINT=tracker_store

COPY credentials.yml endpoints.yml ./
COPY models models

CMD [ "run", "--port", "8080", "--enable-api", "--cors", "*", "--debug"]