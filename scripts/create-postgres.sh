#!/usr/bin/env bash
set -euo pipefail

# Install a lightweight Postgres for local testing and create per-service DBs
# Usage: ./scripts/create-postgres.sh

NAMESPACE=db
RELEASE_NAME=lab-postgres

command -v helm >/dev/null 2>&1 || { echo "helm is required"; exit 1; }

kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install ${RELEASE_NAME} bitnami/postgresql --namespace ${NAMESPACE} \
  --set global.postgresql.postgresqlDatabase=postgres \
  --set postgresqlUsername=labuser \
  --set postgresqlPassword=labpass \
  --set persistence.enabled=false --wait --timeout 2m

echo "Postgres installed in namespace ${NAMESPACE}. To create per-service DBs run the following commands:"
cat <<'EOF'
# run a psql client pod and create DBs/schemas
kubectl run --rm -i --tty --namespace db psql-client --image=bitnami/postgresql -- bash
# then inside the pod:
# psql -h lab-postgres -U labuser -d postgres
# CREATE DATABASE project_service;
# CREATE DATABASE inventory_service;
# CREATE DATABASE contractor_service;
# CREATE DATABASE billing_service;
EOF
