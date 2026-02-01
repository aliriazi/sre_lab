#!/usr/bin/env bash
set -euo pipefail

# Provision Grafana datasources for local lab: Prometheus, Loki, Alertmanager, Tempo
# Usage: ./scripts/provision-grafana-datasources.sh

NAMESPACE=observability
GRAFANA_SVC=lab-prometheus-grafana
LOCAL_PORT=3000

command -v kubectl >/dev/null 2>&1 || { echo "kubectl required"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl required"; exit 1; }

echo "Ensuring Grafana port-forward on http://localhost:${LOCAL_PORT}..."
# start a port-forward in background (if one already exists this will fail silently)
kubectl -n "${NAMESPACE}" port-forward svc/${GRAFANA_SVC} ${LOCAL_PORT}:80 >/dev/null 2>&1 &
sleep 1

GRAFANA_URL="http://localhost:${LOCAL_PORT}"

echo "Retrieving Grafana admin credentials..."
ADMIN_USER=admin
ADMIN_PASSWORD=$(kubectl -n "${NAMESPACE}" get secret ${GRAFANA_SVC} -o jsonpath="{.data.admin-password}" 2>/dev/null || kubectl -n "${NAMESPACE}" get secret lab-prometheus-grafana -o jsonpath="{.data.admin-password}" )
if [ -z "${ADMIN_PASSWORD}" ]; then
  echo "Unable to find Grafana admin password in secrets; aborting"
  exit 1
fi
ADMIN_PASSWORD=$(echo "${ADMIN_PASSWORD}" | base64 --decode)

hdrs=( -u "${ADMIN_USER}:${ADMIN_PASSWORD}" -H "Content-Type: application/json" )

post_datasource() {
  local payload="$1"
  curl -sS "${hdrs[@]}" -X POST "${GRAFANA_URL}/api/datasources" -d "${payload}" || true
}

echo "Provisioning Prometheus datasource..."
post_datasource '{"name":"Prometheus","type":"prometheus","url":"http://lab-prometheus-kube-promet-prometheus.observability.svc.cluster.local:9090","access":"proxy","isDefault":true}'

echo "Provisioning Loki datasource..."
post_datasource '{"name":"Loki","type":"loki","url":"http://lab-loki.observability.svc.cluster.local:3100","access":"proxy"}'

echo "Provisioning Alertmanager datasource..."
post_datasource '{"name":"Alertmanager","type":"alertmanager","url":"http://lab-prometheus-kube-promet-alertmanager.observability.svc.cluster.local:9093","access":"proxy"}'

echo "Provisioning Tempo datasource..."
post_datasource '{"name":"Tempo","type":"tempo","url":"http://lab-tempo.tracing.svc.cluster.local:3200","access":"proxy"}'

echo "Verifying datasources..."
curl -sS "${hdrs[@]}" "${GRAFANA_URL}/api/datasources" | jq -r '.[] | "- \(.name) (\(.type)) -> \(.url)"'

echo "Done. If you don't see expected entries, check Grafana logs and that the services are reachable from Grafana pod." 
