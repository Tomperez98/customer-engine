# customer-engine

customer_engine_api code.

## Docker

```bash
docker build -t customer_engine_api .
docker run -p 8000:8000 --env PORT=8000 --env-file ./.env --rm customer_engine_api
```