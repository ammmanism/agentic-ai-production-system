# Security

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| Prompt injection | Regex + model-based detection (`safety/guards/prompt_injection.py`) |
| PII leakage | Pre-flight scrubbing before storage and LLM calls |
| Toxic content | Two-stage filter: keyword blocklist + Detoxify model |
| Abusive API usage | Token bucket rate limiter per user_id + IP composite key |
| Secret exposure | All secrets via env vars / AWS Secrets Manager — never committed |
| Supply chain | Pinned dependency versions in `pyproject.toml`, checked by Dependabot |
| Audit trail | All LLM inputs logged to S3/BigQuery via structured JSON |

## Secret Management

1. **Local dev**: copy `.env.example` → `.env` and fill in real keys.
2. **CI/CD**: store secrets in GitHub Actions Secrets, injected at runtime.
3. **Production (K8s)**: use `kubectl create secret` or Vault + the Vault sidecar.

## Dependency Security

- `ruff` and `mypy` enforce code quality.
- `.pre-commit-config.yaml` runs `ruff` and `mypy` before every commit.
- Enable GitHub Dependabot for automatic PR updates.

## Network Security

- API runs behind a reverse proxy (NGINX) — never expose uvicorn directly.
- K8s `NetworkPolicy` restricts pod-to-pod traffic to declared routes only.
- Docker sandbox uses `--network=none` and memory limits.

## Incident Response

See [failures.md](failures.md) for past incidents and lessons learned.
