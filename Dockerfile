FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y p7zip-full httrack rsync && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY /app /app
RUN ln -s /dev/shm ram
ENV PYTHONUNBUFFERED 1