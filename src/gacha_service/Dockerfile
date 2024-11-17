FROM python:3.9-slim

WORKDIR /app

COPY ./gacha_service/ .
COPY utils.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["python","-u","main.py"]
