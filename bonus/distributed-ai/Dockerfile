FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

WORKDIR /app

RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.7.1 torchvision==0.22.1

COPY train_mnist.py /app/train_mnist.py

# Bake the dataset into the image so the CCE jobs are reproducible offline.
RUN python -c "from torchvision.datasets import MNIST; MNIST('/data', train=True, download=True); MNIST('/data', train=False, download=True)"

CMD ["python", "/app/train_mnist.py", "--mode", "single"]

