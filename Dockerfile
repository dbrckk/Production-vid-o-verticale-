FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=10000
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY studio.py storyboard.py universal.py cinematic.py scene_backdrops.py kinetic.py geology_premium.py semantic_motion.py motion_layers.py subtitle_design.py narration.py audio_mastering.py soundscape.py qa_video.py editorial.py topic_engine.py generate_topic.py webapp.py ./
COPY web ./web
COPY presets ./presets
# Verify every runtime Python module imports inside the actual deploy image.
RUN python -c "import studio, webapp, cinematic, scene_backdrops, kinetic, geology_premium, semantic_motion, motion_layers, subtitle_design, soundscape, audio_mastering, qa_video, narration"
RUN mkdir -p /app/output && chown -R 10001:10001 /app/output
USER 10001:10001
EXPOSE 10000
CMD ["python", "webapp.py", "--host", "0.0.0.0"]
