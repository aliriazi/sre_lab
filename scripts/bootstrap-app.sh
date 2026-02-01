#!/usr/bin/env bash
set -euo pipefail

# Deploy sample 'construction' microservices (placeholder images) and wait for readiness
# Usage: ./scripts/bootstrap-app.sh

kubectl create namespace app --dry-run=client -o yaml | kubectl apply -f -
# apply apps from repo-root path
kubectl apply -f ./apps/deployments.yaml

echo "Waiting for pods to be ready in namespace 'app'..."
kubectl -n app wait --for=condition=ready pod -l app.kubernetes.io/instance=construction-lab --timeout=120s || true

cat <<EOF
Services deployed in namespace 'app'.
To see pods:
  kubectl -n app get pods
To port-forward the frontend:
  kubectl -n app port-forward svc/frontend 9898:9898
To generate sample traffic, exec a temporary busybox and curl endpoints:
  kubectl run --rm -i --tty --namespace app curl --image=radial/busyboxplus:curl -- sh
  # inside: curl http://project-service:9898/  # or other endpoints
EOF
