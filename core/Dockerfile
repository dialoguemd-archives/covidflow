FROM rasa/rasa:1.9.4-full
EXPOSE 8080

COPY credentials.yml endpoints.yml ./
COPY models models

CMD [ "run", "--port", "8080", "--enable-api", "--cors", "*", "--debug"]
