# Use the official Python image
FROM python:3.9.13 
WORKDIR /app

# Install backend requirements
COPY Backend/requirements.txt /app/
RUN pip install -r requirements.txt

# Install Java
RUN apt-get update && apt-get install -y default-jre

# Copy streaming component
COPY Backend/Streaming /app/streaming

# Copy main.py
COPY Backend/main.py /app/main.py

# Expose ports
EXPOSE 5000
EXPOSE 8102

# Run the backend and streaming apps
CMD java -classpath /app/streaming/feed-play-1.0.jar hackathon.player.Main /app/streaming/dataset.csv 8102 & python main.py
