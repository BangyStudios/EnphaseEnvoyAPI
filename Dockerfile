FROM --platform=linux/amd64 python:3.13-slim

RUN apt-get update && \
    apt-get install -y tzdata cron curl vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV TZ=Australia/Brisbane
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

WORKDIR /eeapi

COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY . .

# Single worker: each worker runs its own poller, so more workers would multiply load on the Envoy.
CMD ["uvicorn", "--factory", "api:create_app", "--host", "0.0.0.0", "--port", "5007", "--workers", "1"]