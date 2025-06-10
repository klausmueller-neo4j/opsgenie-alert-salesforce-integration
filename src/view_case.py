import os, json
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()
sf = Salesforce(
    username=os.getenv("SF_USERNAME"),
    password=os.getenv("SF_PASSWORD"),
    security_token=os.getenv("SF_SECURITY_TOKEN"),
    domain=os.getenv("SF_DOMAIN","test")
)

case_id = "500UN00000C30RDYAZ"

case = sf.Case.get(case_id)

print(json.dumps(case, indent=2))
