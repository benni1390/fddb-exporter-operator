# FDDB Exporter Operator

Kubernetes operator for automated deployment and management of fddb-exporter using Helm charts.

## Overview

This operator automates the deployment of fddb-exporter instances in Kubernetes clusters. It watches for `FddbExporter` custom resources and automatically deploys the fddb-exporter Helm chart with the specified configuration.

## Installation

### Add Helm Repository

```bash
helm repo add benni1390 https://benni1390.github.io/fddb-exporter-deployment
helm repo update
```

### Install CRD

```bash
kubectl apply -f https://raw.githubusercontent.com/benni1390/fddb-exporter-operator/main/deploy/crds/fddbexporter_crd.yaml
```

### Deploy the Operator

```bash
kubectl create namespace fddb-operator-system
helm install fddb-operator benni1390/fddb-exporter-operator \
  --namespace fddb-operator-system
```

### Create an FddbExporter Instance

```bash
kubectl apply -f deploy/examples/fddbexporter_example.yaml
```

## Custom Resource Definition

The operator watches for `FddbExporter` custom resources:

```yaml
apiVersion: fddb.benni1390.github.io/v1alpha1
kind: FddbExporter
metadata:
  name: my-fddb-exporter
  namespace: default
spec:
  helmChart:
    version: "0.0.14"
  image:
    tag: "0.0.1"
  scrapeInterval: "300"
  credentialsSecretName: fddb-credentials
  serviceMonitor:
    enabled: true
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 128Mi
```

## Development

### Run Tests

```bash
make test
```

### Build Docker Image

```bash
make build
```

### Run Locally

```bash
make run-local
```

## Requirements

- Kubernetes cluster with Helm 3 installed
- Credentials stored in Kubernetes secret
