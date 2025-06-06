def handler(event, context):
    # TODO: parse Opsgenie webhook, enrich, call Salesforce
    return {"statusCode": 200, "body": "Hello Opsgenie→SF!"}
