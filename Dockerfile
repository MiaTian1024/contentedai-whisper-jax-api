FROM python:3
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

WORKDIR /usr/src/app

# Install Git
RUN apt-get update && apt-get install -y git

# Install pip
RUN apt-get update && apt-get install -y python3-pip

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install JAX with CUDA support
RUN pip install -U "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

RUN pip install git+https://github.com/sanchit-gandhi/whisper-jax.git

RUN pip install --upgrade --no-deps --force-reinstall git+https://github.com/sanchit-gandhi/whisper-jax.git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]