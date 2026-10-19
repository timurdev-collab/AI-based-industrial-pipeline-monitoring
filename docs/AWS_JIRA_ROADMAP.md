# AWS Cloud architecture roadmap

> **Planning documentation only.** This repository does not claim an active AWS deployment, an active cloud service. Earlier local functionality is unchanged.

## Project
AI-based Industrial Pipeline Monitoring

## Proposed AWS architecture
S3 data archive -> batch model training -> ECR and ECS inference -> CloudWatch alerting

This architecture is a **proposal**, not a deployed service. Some AWS services listed can incur fees. Do not run infrastructure provisioning without an AWS budget, billing alarms, least-privilege credentials and explicit deployment approval. For local development, continue to use the repository's existing documented commands.

## AWS implementation backlog
1. Define resource requirements, least-privilege roles, secrets and budgets.
2. Implement local infrastructure configuration and security checks.
3. Validate cost estimates and deployment procedures before provisioning.
4. Deploy only after explicit authorization; document reproducibility and monitoring.

**Current status:** AWS architecture is planned, not deployed.
