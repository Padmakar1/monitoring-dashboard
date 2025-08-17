# Monitoring and Logging Dashboard (local demo)

This project provides a local demo stack using Docker Compose to showcase monitoring (Prometheus + Grafana) and logging (ELK: Elasticsearch, Logstash, Kibana) for a sample Python Flask app.

Prerequisites

- Docker Desktop (Windows) installed and running
- At least 4GB free RAM; Elasticsearch will need memory
- Optional: docker-compose v1 or Docker Compose v2 via the Docker CLI

Quick start

1. From this folder run:

   docker compose up --build

2. Services:
    - App: http://localhost:8000
       - endpoints: `/`, `/item/<name>`, `/error`, `/metrics`
    - Prometheus: http://localhost:9090
    - Grafana: http://localhost:3000 (admin/admin)
    - Kibana: http://localhost:5601
    - Elasticsearch: http://localhost:9200
    - Alertmanager: http://localhost:9093

Notes

- Filebeat ships logs from `app` to Logstash which writes to Elasticsearch.
- Grafana is provisioned with Prometheus and Elasticsearch datasources and a simple dashboard.
 - Prometheus alert rules are in `prometheus/rules/alerts.yml`. Alerts:
    - `AppDown` when the `app` target is down for >1m
    - `HighLatency` when p95 latency > 1s for 2m
 - Alertmanager is provisioned at `alertmanager/config.yml` and listens on port 9093.

Testing alerts

 - To trigger errors: visit `http://localhost:8000/error`.
 - To simulate higher latency you can add more sleep in the app or run load against `/item/<name>`.

Troubleshooting

- If Elasticsearch fails to start due to memory, increase Docker Desktop memory or reduce ES_JAVA_OPTS.
- If ports are in use, stop conflicting services or change ports in `docker-compose.yml`.

Alertmanager credentials & testing

- Slack: open `alertmanager/config.yml` and replace the `api_url` with your Slack incoming webhook URL. Keep secrets out of VCS — use environment variables or a secrets manager for production.
- SMTP: set `smtp_smarthost`, `smtp_from`, `smtp_auth_username`, and `smtp_auth_password` in `alertmanager/config.yml` or supply them through environment variables when running Alertmanager.
- MS Teams: replace the `webhook` URL in `alertmanager/config.yml` for the `msteams-webhook` receiver.

Local test scripts (run after Alertmanager is up):

```powershell
# send a test alert
python alertmanager\send_test_alert.py

# create a silence for the TestAlert
python alertmanager\create_silence.py
```

Applying index template for logs to Elasticsearch (optional):

```powershell
curl -XPUT "http://localhost:9200/_index_template/app-logs-template" -H "Content-Type: application/json" -d @logstash\log_index_template.json
```

Security note: Do not commit real credentials. Use environment variables, Docker secrets, or a dedicated secrets manager when wiring real Slack/SMTP credentials.

Using Docker secrets (example)

This repo includes an example that uses Docker Compose secrets for Alertmanager. The compose file references files under `alertmanager/secrets/`. Fill those files with your real webhook/credentials (or use Docker secrets in your production environment) and ensure `alertmanager/secrets/.gitignore` is present to avoid committing them.

To start with secrets in Compose (Docker Desktop):

```powershell
docker compose up --build -d
```

Alertmanager's entrypoint will substitute secret file contents into the generated config at `/etc/alertmanager/config.yml`.

Continuous Integration

This repo includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs unit tests and a lightweight integration job which starts a minimal subset of services (Prometheus, Alertmanager, app) and triggers a test alert. The integration job requires Docker support on the runner.

Grafana alerting

Grafana is provisioned with a notifier that posts to Alertmanager and a couple of example alert rules in `grafana/provisioning/alerting/alerting_rules.yml`. You can edit those rules and provision contact points under `grafana/provisioning/notifiers`.
