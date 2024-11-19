FROM python:3.9-slim

WORKDIR /app

COPY ./currency_service .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8004

CMD ["python","-u","main.py"]
