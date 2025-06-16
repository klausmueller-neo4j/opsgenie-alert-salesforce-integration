# Opsgenie → Salesforce Integration

This service receives Opsgenie webhooks for “out of disk” alerts, enriches them with customer details from Neo4j Aura, and automatically creates Proactive Cases in Salesforce.

## Local Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/klausmueller-neo4j/opsgenie-alert-salesforce-integration
   cd opsgenie-alert-salesforce-integration
   ```

2. **Activate the virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Copy and edit `.env`**

   ```bash
   cp .env.example .env
   # then edit .env and fill in:
   # SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, SF_DOMAIN
   # NEO4J_URI, NEO4J_TOKEN
   ```

---

## Running Locally

Start the FastAPI+Uvicorn server:

```bash
uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Testing with `curl`

Send a sample Opsgenie webhook payload:

```bash
curl -X POST http://localhost:8000/opsgenie-alert \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "0.ntetsbj47wg0",
    "message": "Neo4j Disk Usage: 90%",
    "description": "Database ID: `2d9e2550`\nPriority: `highest`\nTier: `enterprise`",
    "details": {"severity": "Error"}
  }'
```

Expected response:

```json
{ "statusCode": 201, "body": "{ \"status\": \"created\", \"caseId\": \"...\" }" }
```

---

The service will:

1. Extract **Database ID**, **Tier**, **Priority** from `description`.
2. Query Neo4j for owner email & customer profile ID.
3. Check for existing open case in Salesforce.
4. Create a new Case in Salesforce if none exists.

That's it! 🎉
