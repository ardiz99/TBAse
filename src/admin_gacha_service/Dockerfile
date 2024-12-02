FROM python:3.9-slim

WORKDIR /app

COPY ./admin_gacha_service/main.py ./app.py
COPY ./admin_gacha_service/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8006

CMD ["flask", "run", "--host=0.0.0.0", "--port=8006", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
