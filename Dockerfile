# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# system deps for some libs
RUN apt-get update && apt-get install -y build-essential libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OLLAMA_API=http://host.docker.internal:11434

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
