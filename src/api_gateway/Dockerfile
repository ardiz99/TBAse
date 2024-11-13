# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /PROGETTO

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the necessary port
EXPOSE 8000

# Run the API gateway
CMD ["python", "main.py"]
