FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY /app /app
RUN ln -s /dev/shm temp
ENV PYTHONUNBUFFERED 1