# Opsgenie → Salesforce Integration

This service receives Opsgenie webhooks for “out of disk” alerts, enriches them with customer details, and automatically creates Proactive Cases in Salesforce.

## Local Setup

1. Activate the virtualenv:  
   ```
   source venv/bin/activate
   ```

2. Install dependencies:  
   ```
   pip install -r requirements.txt
   ```

3. Copy and edit `.env` with your credentials:  
   ```
   cp .env.example .env
   # then open .env and fill in SF_USERNAME, SF_PASSWORD, etc.
   ```

4. Run locally via AWS SAM or your chosen framework.

## Deployment



