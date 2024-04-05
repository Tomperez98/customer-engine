FROM python:3.12-slim-bullseye

EXPOSE $PORT

WORKDIR /app
COPY . ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock
CMD uvicorn customer_engine_api.api:app --host 0.0.0.0 --port $PORT
