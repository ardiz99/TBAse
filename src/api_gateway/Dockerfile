FROM python:3.9-slim

WORKDIR /app

COPY ./api_gateway/main.py ./app.py
COPY ./api_gateway/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

<<<<<<< HEAD
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
=======
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000", "--cert=/run/secrets/certificate", "--key=/run/secrets/key"]
>>>>>>> origin
