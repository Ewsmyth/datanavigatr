# Use a lightweight Python image
FROM python:3.9-slim

# Set environment variables to avoid Python bytecode generation and ensure output is flushed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set a working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app/

# Expose the port for the app (matching the port set in the Flask app config)
EXPOSE 80

# Define environment variables for secrets and configurations (optional, can be passed at runtime)
ENV SQLALCHEMY_DATABASE_URI="sqlite:////var/lib/docker/volumes/datanavigatr-data/data-navi-gatr-data.db"
ENV SQLALCHEMY_BINDS_QDB1="sqlite:////var/lib/docker/volumes/qdb1-data/qdb1.db"
ENV SQL_QUERY_DIR="/var/lib/docker/volumes/sql-queries/"
ENV DOWNLOADED_DB_PATH="/var/lib/docker/volumes/downloaded-data/"
ENV DOWNLOADED_MEDIA_PATH="/var/lib/docker/volumes/downloaded-media/"
ENV HOST="0.0.0.0"
ENV PORT=80

# Start Gunicorn to serve the application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]
