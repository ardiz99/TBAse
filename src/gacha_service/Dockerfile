FROM python:3.9-slim

WORKDIR /app

COPY ./gacha_service/main.py ./app.py
COPY ./gacha_service/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8002

CMD ["flask", "run", "--host=0.0.0.0", "--port=8002", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]