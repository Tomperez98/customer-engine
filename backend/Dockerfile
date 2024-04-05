FROM python:3.12-slim-bullseye

EXPOSE $PORT

WORKDIR /app
COPY . ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock
CMD gunicorn customer_engine_api.api:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --log-level=info

