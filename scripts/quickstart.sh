#!/usr/bin/env bash
set -euo pipefail

# Quickstart: create kind cluster and install observability components (idempotent)
# Usage: ./scripts/quickstart.sh

RELEASE_PREFIX="lab"
CLUSTER_NAME="lab"
KIND_CONFIG="kind-config.yaml"

command -v kind >/dev/null 2>&1 || { echo "kind is required"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "helm is required"; exit 1; }

echo "Creating kind cluster '${CLUSTER_NAME}' (if not exists)..."
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind create cluster --name "${CLUSTER_NAME}" --config "${KIND_CONFIG}"
else
  echo "Cluster ${CLUSTER_NAME} already exists"
fi

echo "Adding helm repos..."
helm repo add grafana https://grafana.github.io/helm-charts || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts || true
helm repo add bitnami https://charts.bitnami.com/bitnami || true
helm repo update

echo "Creating namespaces..."
kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace tracing --dry-run=client -o yaml | kubectl apply -f -

echo "Installing/upgrading kube-prometheus-stack (Prometheus + Grafana)..."
helm upgrade --install ${RELEASE_PREFIX}-prometheus prometheus-community/kube-prometheus-stack \
  --namespace observability --wait --timeout 5m

echo "Installing/upgrading OpenTelemetry Collector..."
# use repo-root relative path to values file
if [ -f ./otel-values.yaml ]; then
  OTEL_VALUES="./otel-values.yaml"
else
  OTEL_VALUES=""
fi
if [ -n "${OTEL_VALUES}" ]; then
  helm upgrade --install ${RELEASE_PREFIX}-otel open-telemetry/opentelemetry-collector \
    --namespace observability -f "${OTEL_VALUES}" --wait --timeout 3m || true
else
  helm upgrade --install ${RELEASE_PREFIX}-otel open-telemetry/opentelemetry-collector \
    --namespace observability --wait --timeout 3m || true
fi

echo "Installing/upgrading Loki and Tempo (optional)..."
helm upgrade --install ${RELEASE_PREFIX}-loki grafana/loki-stack --namespace observability --wait --timeout 2m || true
helm upgrade --install ${RELEASE_PREFIX}-tempo grafana/tempo --namespace tracing --wait --timeout 2m || true

echo "Done. Wait a few moments for pods to be ready."

cat <<EOF
Next steps:
  - kubectl -n observability get pods
  - kubectl -n observability port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
  - kubectl -n observability port-forward svc/prometheus-grafana 3000:80
  - ./scripts/create-postgres.sh   # to install a local Postgres for services
  - ./scripts/bootstrap-app.sh    # to deploy the sample construction app
EOF
