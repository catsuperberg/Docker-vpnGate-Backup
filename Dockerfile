FROM python:slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

FROM python:slim
WORKDIR /app
COPY --from=build /app /
RUN ln -s /dev/shm temp
ENV PYTHONUNBUFFERED 1
CMD ["python", "vpn_backup_daemon.py"]