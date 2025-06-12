# src/app.py
import os
import json
from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
import logging
from neo4j import GraphDatabase, bearer_auth
import re


# Load from .env when running locally
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize SF connection once per container
sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain=os.getenv("SF_DOMAIN", "login"),
)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_TOKEN = os.getenv("NEO4J_TOKEN")

# 1) Case Subject is static in this scenario
CASE_SUBJECT = (
    "Neo4j Support: URGENT: ACTION REQUIRED - " "Database instance over storage limit - {dbid}"
)

# 2) Case Description with placeholders for email and dbid
CASE_DESCRIPTION = """\
Hi {email}

Our regular monitoring of your instance has detected that you are extremely close to the capacity 
of the physical storage associated with your database instance **{dbid}**

# Your disk usage is at a CRITICAL level – Action` is required immediately

The disk metric in the Aura console is over 100% usage but because we have built in some safety 
margin, your instance is for now still able to operate. **Your involvement is now essential.**

We may have reached out to you previously to indicate you were at a high level of risk to fill up 
the disk and **we now urge you to act fast now (final notification).**

If you reach 100% of the physical disk, **your instance will go into a read-only mode** and all 
new write operations will fail. We placed this last resort safety in an attempt to protect the 
integrity of your data and limit the damage incurred.

**One of the following actions is required** to prevent data corruption/loss and ensure the 
continuation of smooth operations going forward:

- Reduce, limit or stop the data ingestion or any write query that could require any additional 
  storage (new nodes or relationships as well as new properties or creating new index etc…)  
- Resize the instance to a larger instance, as outlined in the knowledge base article  
  Resize your Neo4j AuraDB instance  
  (https://aura.support.neo4j.com/hc/en-us/articles/1500000954301-Resize-your-Neo4j-AuraDB-Instance).  
  Note that this can take longer than usual as you are loading additional data.

For reference, please note that you can monitor storage usage within the Aura console as explained here:  
https://support.neo4j.com/s/article/5111886576275-Monitoring-Aura-Database-From-Console-Metrics

**NOTE:** Deleting nodes/relationships will _not_ reduce your disk footprint or the metrics reported.  
To reclaim space you must perform an offline store compaction. See:  
https://aura.support.neo4j.com/hc/en-us/articles/4408091782675-How-to-compact-your-database-store

Regards,
"""

PACKAGE_MAP = {
    "enterprise": "AuraDB Virtual Dedicated Cloud",
    "professional": "AuraDB Professional",
    "mte": "AuraDB Business Critical"
}

driver = GraphDatabase.driver(NEO4J_URI, auth=bearer_auth(NEO4J_TOKEN))


def build_case_payload(
    email: str, dbid: str, cpp_id: str, severity: str, package_edition: str
):
    description = CASE_DESCRIPTION.format(email=email, dbid=dbid)
    subject = CASE_SUBJECT.format(dbid=dbid)
    return {
        "Subject": subject,
        "Description__c": description,
        "Customer_Project_Profile__c": cpp_id,
        "Severity__c": severity,
        "Database_ID_DBID__c": dbid,
        "Brand__c": "Neo4j Aura",
        "Was_existing_documentation_used__c": "Yes, adding link to existing doc below",
        "Component__c": "Storage",
        "Neo4   j_Package_Edition__c": package_edition,
        "Product_Surface__c": "Aura Console",
        "Operations__c": "Aura",
        "Admin__c": "Proactive",
        "External_Doc_Used_to_Resolve__c": "https://support.neo4j.com/hc/en-us/articles/1500000954301-Resize-your-Neo4j-AuraDB-Instance",
    }


def get_dbid(description: str):
    m = re.search(r"Database ID:\s*`([^`]+)`", description)
    if m:
        return m.group(1)
    else:
        return ""


def get_tier(desciption: str):
    m_tier = re.search(r"Tier:\s*`([^`]+)`", desciption)
    if m_tier:
        return m_tier.group(1).lower() if m_tier else None
    else:
        return ""


def handler(event, context):

    logger.debug("Lambda invoked—event: %s", json.dumps(event))

    payload = json.loads(event.get("body", "{}"))
    alert_descripion = payload.get("description", "")
    tier = get_tier(alert_descripion)
    db_id = get_dbid(alert_descripion)
    severity = "Severity 3"

    soql = (
        "SELECT Id "
        "FROM Case "
        f"WHERE Subject = '{CASE_SUBJECT}' "
        f"  AND Database_ID_DBID__c = '{db_id}' "
        "  AND Status != 'Closed' "
        "LIMIT 1"
    )
    existing = sf.query(soql)

    logger.debug("Salesforce query for existing case returned: %s", existing)
    if existing["totalSize"] > 0:
        logger.info("Case already exists for dbid %s", db_id)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"status": "exists", "caseId": existing["records"][0]["Id"]}
            ),
        }

    with driver.session(database="neo4j") as session:
        rec = session.run(
            """
            MATCH (d:Database {key:$db_id})<-[:OWNS]-(u:User)
            WITH d,u
            MATCH (d)<-[:CONTAINS]-(n:Namespace)
            RETURN u.email as email, n.salesforce_customer_project_profile_id as cpp_id
        """,
            db_id=db_id,
        ).single()

    if not rec:
        logger.error("No email found for database %s", db_id)
        return {
            "statusCode": 404,
            "body": json.dumps(
                {"status": "error", "message": f"No owner for database {db_id}"}
            ),
        }

    email = rec["email"]
    cpp_id = rec["cpp_id"]
    logger.info("Database %s is owned by %s", db_id, email)

    # Build the Case

    package_edition = PACKAGE_MAP.get(tier)

    case_data = build_case_payload(
        email=email,
        dbid=db_id,
        cpp_id=cpp_id,
        severity=severity,
        package_edition=package_edition,
    )
    logger.debug("Creating new case with data: %s", case_data)
    try:
        result = sf.Case.create(case_data)
        logger.info("Salesforce create() returned: %s", result)
    except SalesforceMalformedRequest as e:
        logger.error("Salesforce create() error: %s", e, exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": str(e),
                }
            ),
        }

    return {
        "statusCode": 201,
        "body": json.dumps({"status": "created", "caseId": result["id"]}),
    }
