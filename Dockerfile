# Use the official Python slim image. 
# (Slim is preferred over Alpine for Python to avoid compiling C-extensions from source)
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files 
# and to ensure output is sent straight to the terminal without buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for PostgreSQL (psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port Django runs on
EXPOSE 8000

# The command to run when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]