FROM python:3.11-slim

WORKDIR /app

COPY chatvgp/backend/requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

COPY chatvgp/backend .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker"]
