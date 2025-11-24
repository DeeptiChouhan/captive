FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# create reports dir (mounted from host)
RUN mkdir -p /app/reports

ENV PYTHONUNBUFFERED=1

# default command overridden by docker-compose for backend/worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
