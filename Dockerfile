FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fddb_operator.py .

RUN helm repo add benni1390 https://benni1390.github.io/fddb-exporter-deployment && \
    helm repo update

CMD ["kopf", "run", "fddb_operator.py", "--verbose"]
