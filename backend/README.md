# customer-engine

Backend code.

## Docker

```bash
docker build -t backend .
docker run -p 8000:8000 --env PORT=8000 --env-file ./.env --rm backend
```