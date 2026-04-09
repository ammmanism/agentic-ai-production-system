# Security Policy

## Supported Versions

Currently, only the `main` branch is supported with security updates.

## Reporting a Vulnerability

We take the security of this agentic production system seriously. If you believe you have found a security vulnerability (such as a prompt injection bypass or PII leakage bug), please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please email the project maintainer at `security@example.com`.

You should receive a response within 48 hours. If for some reason you do not, please try pinging the repository maintainers privately.

## Threat Model

We assume that:
1. End users are actively trying to breach the system via complex adversarial prompt injections.
2. Attackers might attempt context poisoning by injecting malicious payloads into retrievable documents.
3. Strict rate limiting using the IP and API keys must be enforced at the middleware layer.
