"""
This module is responsible for sending a response to Cloud Formation
"""

import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUCCESS = "SUCCESS"
FAILED = "FAILED"

def send(event, context, response_status, response_data, physical_resource_id=None, no_echo=False):
    "A function to send a response to Cloud Formation"
    if "ResponseURL" not in event:
        logger.error("Error: ResponseURL is missing in the event.")
        raise ValueError("Error: ResponseURL is missing in the event.")

    response_url = event["ResponseURL"]

    response_body = {
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": physical_resource_id or context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "NoEcho": no_echo,
        "Data": response_data
    }

    json_response_body = json.dumps(response_body)

    headers = {
        "content-type": "",
        "content-length": str(len(json_response_body))
    }

    try:
        response = requests.put(response_url, data=json_response_body,headers=headers, timeout=10)
        logger.info("Status code: %s", response.reason)
    except Exception as e:
        logger.error("send(..) failed executing http.request(..): %s", str(e))
