# DOCKERFILE 

FROM pytorch/pytorch:2.5.0-cuda12.4-cudnn9-devel

WORKDIR /app


RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ENV CUDA_HOME=/usr/local/cuda


RUN pip install --no-cache-dir \
    torch==2.5.0+cu124 \
    torchvision==0.20.0+cu124 \
    torchaudio==2.5.0+cu124 \
    --index-url https://download.pytorch.org/whl/cu124

# CUDA 12.4
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcudnn9-cuda-12 \
    libcudnn9-dev-cuda-12 \
    && ldconfig && rm -rf /var/lib/apt/lists/*

# Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --no-deps

COPY requirements-audio.txt .
RUN pip install --no-cache-dir -r requirements-audio.txt --no-deps


COPY . .

EXPOSE 8000


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]