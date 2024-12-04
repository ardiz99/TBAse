FROM python:3.9-slim

WORKDIR /app

COPY ./currency_service/main.py ./app.py
COPY ./currency_service/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8004

<<<<<<< HEAD
CMD ["flask", "run", "--host=0.0.0.0", "--port=8004", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
=======
CMD ["flask", "run", "--host=0.0.0.0", "--port=8004", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
>>>>>>> origin
