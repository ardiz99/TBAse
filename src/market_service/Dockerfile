FROM python:3.9-slim

WORKDIR /app

COPY ./market_service/main.py ./app.py
COPY ./market_service/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8003

CMD ["flask", "run", "--host=0.0.0.0", "--port=8003", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]