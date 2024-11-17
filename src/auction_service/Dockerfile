FROM python:3.9-slim

WORKDIR /app

COPY ./auction_service .
COPY utils.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["python","-u","main.py"]
