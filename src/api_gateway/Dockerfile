FROM python:3.9-slim

WORKDIR /app

COPY ./api_gateway .
COPY utils.py /app/utils.py

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python","-u","main.py"]
