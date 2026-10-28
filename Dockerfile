FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=10000
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY studio.py storyboard.py universal.py topic_engine.py generate_topic.py webapp.py ./
COPY web ./web
COPY presets ./presets
RUN mkdir -p /app/output && chown -R 10001:10001 /app/output
USER 10001:10001
EXPOSE 10000
CMD ["python", "webapp.py", "--host", "0.0.0.0"]
