FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install postgresql related dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Install any needed packages specified in requirements.txt + the special Python tagme module
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/alabeybahri/tagme-python.git@aceca09c3cf0aa5eb1a90d8f02472230e57a8a3e

# Install the spaCy model (replace en_core_web_sm)
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download en_core_web_sm

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service-account-file.json"

# Copy the service account key file into the container
COPY service-account-file.json /app/service-account-file.json

# Run main.py when the container launches
CMD ["python", "main.py"]
