FROM python:3.9-slim

WORKDIR /app

COPY ./db_manager/main.py ./app.py
COPY ./db_manager/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8005

CMD ["flask", "run", "--host=0.0.0.0", "--port=8005", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
