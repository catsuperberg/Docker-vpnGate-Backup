FROM python:3.9-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

FROM python:3.9-slim
WORKDIR /
COPY --from=build /app .
ENV PYTHONUNBUFFERED 1
CMD ["python", "./vpn_backup_daemon.py"]