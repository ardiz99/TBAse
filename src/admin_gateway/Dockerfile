<<<<<<< HEAD
FROM python:3.9-slim

WORKDIR /app

COPY ./admin_gateway/main.py ./app.py
COPY ./admin_gateway/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
=======
FROM python:3.9-slim

WORKDIR /app

COPY ./admin_gateway/main.py ./app.py
COPY ./admin_gateway/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
>>>>>>> origin
