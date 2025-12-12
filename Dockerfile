FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for some parsing libs)
RUN apt-get update && apt-get install -y git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory structure inside container
RUN mkdir -p /data/raw_novels /data/final_novels

# Expose NiceGUI port
EXPOSE 8080

CMD ["python", "app/main.py"]