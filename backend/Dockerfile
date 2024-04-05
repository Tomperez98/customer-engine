FROM python:3.12-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/usr/local/
RUN apt-get update && apt-get -y upgrade && apt-get clean

COPY . .

RUN pip install -U uv
RUN uv venv
RUN uv pip install -r requirements.lock
RUN uv pip install -e .
RUN uv clean

EXPOSE $PORT

CMD gunicorn customer_engine_api.api:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --log-level=info

