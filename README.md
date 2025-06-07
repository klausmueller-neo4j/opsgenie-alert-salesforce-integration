# Opsgenie → Salesforce Integration

This service receives Opsgenie webhooks for “out of disk” alerts, enriches them with customer details, and automatically creates Proactive Cases in Salesforce.

## Local Setup

1. **Activate the virtualenv:**

   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Copy and edit `.env` with your credentials:**

   ```bash
   cp .env.example .env
   # then open .env and fill in SF_USERNAME, SF_PASSWORD, etc.
   ```

4. **Run locally via AWS SAM or your chosen framework.**

   **If you’re on macOS using Docker Desktop, export the Docker socket before running SAM:**

   ```bash
   export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
   ```

## Deployment

*TODO: add your SAM/GitHub Actions/Cloud Run deploy instructions here.*
