FROM python:3.11-slim

# Makes sure that logs are shown immediately
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Watchfiles from uvicorn[standard] breaks reload inside Docker as per docker-compose.yaml setup (macOS)
# watchgod fixes it
RUN pip uninstall watchfiles -y && \
    pip install watchgod==0.8.2

COPY ./app /app

EXPOSE 8000

CMD ["gunicorn", "app.main:sio_app", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--workers", "1", \
     "--worker-class", "uvicorn.workers.UvicornWorker"]
