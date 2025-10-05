# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/

# Set environment variables (optional defaults)
ENV PYTHONUNBUFFERED=1

# Run the script
CMD ["python", "app/main.py"]