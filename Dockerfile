FROM python:3
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04


# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

RUN pip install -U "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

RUN pip install git+https://github.com/sanchit-gandhi/whisper-jax.git

RUN pip install --upgrade --no-deps --force-reinstall git+https://github.com/sanchit-gandhi/whisper-jax.git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables if needed
ENV CUDA_PATH="/usr/local/cuda"

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]