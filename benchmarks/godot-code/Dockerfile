FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfontconfig1 libfreetype6 libx11-6 libxrandr2 libxi6 \
    libxcursor1 libxinerama1 libxext6 libgl1 libasound2t64 \
    libpulse0 libudev1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/tmp
ENV XDG_CONFIG_HOME=/tmp
ENV XDG_DATA_HOME=/tmp
WORKDIR /project
