# syntax=docker/dockerfile:1

FROM python:3.10-slim AS builder


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.10-slim


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


RUN addgroup --system appuser && adduser --system --ingroup appuser appuser


WORKDIR /app

# Copy only necessary files from builder stage to keep image size small
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


COPY . .


USER appuser

# Expose the port that the FastAPI app will run on
EXPOSE 8000

# Command to start the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
