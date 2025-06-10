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

4. **Export Docker socket (macOS + Docker Desktop):**

   ```bash
   export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
   ```

## Build & Run Locally

After completing the Local Setup, build and start the local API emulator:

1. **Build the project:**

   ```bash
   sam build
   ```

2. **Start the local API Gateway emulator:**

   ```bash
   sam local start-api --port 3000
   ```

3. **Invoke the function via curl (in a new terminal):**

   ```bash
   curl -X POST http://127.0.0.1:3000/opsgenie-alert \
     -H "Content-Type: application/json" \
     -d '{
       "alias": "test-alert-001",
       "message": "Test Case Creation from curl",
       "entity": "production-orch-0375",
       "details": {
         "usage": "92%",
         "note": "This is just a test payload"
       }
     }'
   ```

## Deployment

*TODO: add your SAM/GitHub Actions/Cloud Run deploy instructions here.*
