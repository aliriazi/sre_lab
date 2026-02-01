Project: Local Kubernetes Observability Lab

Overview
--------
This repository contains configuration snippets and notes to run a local observability lab on a Kubernetes cluster (Kind). The lab demonstrates a simple microservice application stack instrumented for metrics, logs, and traces using Prometheus, Grafana, Loki, Jaeger/Tempo, and the OpenTelemetry Collector. ArgoCD is recommended as the GitOps deployment engine for the lab.

Goals
-----
- Provide a repeatable local environment for learning and demos
- Show end-to-end telemetry (metrics, logs, traces) and correlation
- Use GitOps (ArgoCD) for reproducible deployments

Prerequisites
-------------
- macOS or Linux with Docker installed and running
- `kind` (Kubernetes in Docker)
- `kubectl` configured to talk to your cluster
- `helm` for chart installs

Quickstart (minimal)
---------------------
Create a Kind cluster using the included `kind-config.yaml`:

```bash
kind create cluster --name lab --config kind-config.yaml
```

Add required Helm repositories and install the observability stack (examples):

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack --namespace observability --create-namespace

# Install OpenTelemetry Collector (example)
helm install otel open-telemetry/opentelemetry-collector --namespace observability

# Install Loki and Tempo (optional)
helm install loki grafana/loki-stack --namespace observability
kubectl create namespace tracing || true
helm install tempo grafana/tempo --namespace tracing
```

Port-forwarding & Access
------------------------
Grafana (example):

```bash
kubectl --namespace observability get pods -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=prometheus" -o name
kubectl -n observability port-forward svc/prometheus-grafana 3000:80
# then open http://localhost:3000
```

Prometheus UI:

```bash
kubectl -n observability port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
# then open http://localhost:9090
```

OpenTelemetry Collector metrics (scrape endpoint exposed in `otel-values.yaml` at 8889):

```bash
kubectl -n observability port-forward svc/otel-opentelemetry-collector 8889:8889
curl -s localhost:8889/metrics | head
```

Verification
------------
- Check pods and namespaces are ready:

```bash
kubectl get ns
kubectl -n observability get pods
```

- Confirm Grafana admin password (example):

```bash
kubectl --namespace observability get secret prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

OTEL & ServiceMonitor notes
---------------------------
- The repository includes `otel-values.yaml` (values for the collector). It exposes a Prometheus scrape endpoint on port `8889` by default.
- `otel-servicemonitor.yaml` uses a selector with `app.kubernetes.io/name: opentelemetry-collector`. Ensure the deployed collector has matching labels, otherwise Prometheus will not discover the endpoint.
- Decide between a central OTEL gateway (recommended for this lab) or per-app sidecars depending on the learning goals.

Suggested GitHub repository layout
---------------------------------
- `infra/` — Helm values, `kind-config.yaml`, and ArgoCD App-of-Apps manifests
- `apps/` — sample microservices (manifests or Helm charts)
- `observability/` — `otel-values.yaml`, `otel-servicemonitor.yaml`, dashboards, and alerts
- `docs/` — runbook, demo scripts, and architecture notes
- `README.txt` — this file (quickstart and references)

CI / Validation suggestions
-------------------------
- Add lightweight GitHub Actions that run:
  - YAML linting (`yamllint` / `kubeval`)
  - `helm template` for charts
  - Optional: spin up `kind` and run smoke tests (deploy + basic checks)

Troubleshooting & common pitfalls
--------------------------------
- Label mismatches: ServiceMonitor selectors must match target labels.
- High-cardinality metrics: keep example metrics low-cardinality to avoid local Prometheus blowups.
- Resource limits: lower resource requests/limits for laptop testing; increase when doing load tests.

Next steps (recommended)
------------------------
- Add a `LICENSE` and short `CONTRIBUTING.md`.
- Expand `docs/` with step-by-step ArgoCD App-of-Apps example.
- Optionally add a `Makefile` or small `scripts/` folder with convenience commands to boot the stack and run smoke tests.

Contacts
--------
This is a personal lab repository. For questions or changes, update the repo or open an issue in the GitHub repo.

Apps quickstart
---------------
To deploy the sample `construction` microservices and exercise telemetry, use the helper scripts in `scripts/`:

1. Boot cluster and observability stack:

```bash
./scripts/quickstart.sh
```

2. (Optional) Install a lightweight Postgres and create per-service DBs:

```bash
./scripts/create-postgres.sh
# then follow the printed psql instructions to create databases for each service
```

3. Deploy the sample construction app:

```bash
./scripts/bootstrap-app.sh
```

4. Verify services and generate traffic:

```bash
kubectl -n app get pods,svc
kubectl -n app port-forward svc/frontend 9898:9898
# use a temporary pod to curl internal services
kubectl -n app run --rm -i --tty curl --image=radial/busyboxplus:curl -- sh
```

Notes
-----
- Scripts assume you run them from the repository root. They are idempotent and will skip actions that already exist.
- If `kind`, `kubectl`, or `helm` are missing the scripts will exit with an error; install them first.

Next steps
----------
- After deploying, check Grafana, Prometheus, Loki, and Tempo UIs via port-forwarding outlined earlier in this README.
- See `apps/deployments.yaml` for labels (ServiceMonitor discovery) and replace placeholder images with your services when ready.
