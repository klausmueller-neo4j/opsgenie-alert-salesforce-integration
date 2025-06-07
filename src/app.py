# src/app.py
import os
import json
from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
import logging


# Load from .env when running locally
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize SF connection once per container
sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain=os.getenv("SF_DOMAIN", "login")
)

def handler(event, context):
    
    logger.debug("Lambda invoked—event: %s", json.dumps(event))

    payload = json.loads(event.get("body", "{}"))
    
    logger.debug("Parsed payload: %s", payload)
    
    # TODO: replace this stub with your real enrichment lookup
    lookup = {"AccountId": "001gL000008TxxmQAC"}
    
    # Idempotency check
    alias = payload.get("alias")
    existing = sf.query(
        f"SELECT Id FROM Case WHERE CaseNumber='{alias}' LIMIT 1"
    )
    
    logger.debug("Salesforce query for existing case returned: %s", existing)
    if existing["totalSize"] > 0:
        logger.info("Case already exists for alias %s", alias)
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "exists", "caseId": existing["records"][0]["Id"]})
        }

    # Build the Case
    case_data = {
        "Subject": f"[Auto] {payload.get('message')}",
        "Description": json.dumps(payload.get("details", {})),
        "Origin": "Opsgenie",
        "AccountId": lookup["AccountId"]
    }
    logger.debug("Creating new case with data: %s", case_data)
    try:
        result = sf.Case.create(case_data)
        logger.info("Salesforce create() returned: %s", result)
    except SalesforceMalformedRequest as e:
        logger.error("Salesforce create() error: %s", e, exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e),
            })
        }

    return {
        "statusCode": 201,
        "body": json.dumps({"status": "created", "caseId": result["id"]})
    }