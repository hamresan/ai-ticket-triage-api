# Security

## Reporting a vulnerability

Please do not open a public issue containing exploit details, credentials, customer data, or other sensitive material. Use GitHub's private vulnerability reporting for this repository when available.

## Security model

This repository is a reference implementation, not a complete internet-facing support platform. Before production use, add authentication, authorization, rate limiting, abuse controls, retention/deletion policy, transport security, secret management, and deployment-specific database controls.

Provider output is treated as untrusted and validated before persistence. Suggested replies are drafts only and are never sent automatically.

Normal application logs intentionally exclude ticket subject/message, prompts, credentials, idempotency keys, raw provider output, and provider/database stack details.

## Secrets

Never commit provider API keys or real customer data. Keep local secrets in an untracked `.env` file or a deployment secret manager. The Fake provider requires no credentials and is the recommended default for tests and demonstrations.
