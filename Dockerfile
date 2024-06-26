FROM python:3.11-slim
# get BOT_NAME from .env !
ENV BOT_NAME=mybotname

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /usr/src/app/${BOT_NAME}

COPY requirements.txt /usr/src/app/${BOT_NAME}
RUN pip install -r /usr/src/app/${BOT_NAME}/requirements.txt
COPY . /usr/src/app/${BOT_NAME}
