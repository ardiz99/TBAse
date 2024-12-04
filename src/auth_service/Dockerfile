FROM python:3.9-slim

WORKDIR /app

COPY ./auth_service/main.py ./app.py
COPY ./auth_service/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8001

CMD ["flask", "run", "--host=0.0.0.0", "--port=8001", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
