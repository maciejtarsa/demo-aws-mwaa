"""
Lambda handler body
"""

import logging
from uuid import uuid4

import _cfnresponse
from _log_groups import tag_log_group
from _vpc_endpoints import create_vpc_endpoint, delete_vpc_endpoints, get_ips_from_endpoint

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    "Lambda handler function"
    try:
        request_type = event["RequestType"]
        logger.info("request type is: %s", request_type)
        # pass resource id to all responses to prevent deletion when updating
        resource_id = event.get("PhysicalResourceId", str(uuid4()))
        input_data = event.get("ResourceProperties", {})
        log_group_arns = input_data.get("LogGroupArns")
        vpc_id = input_data.get("VpcId")
        vpc_service_database = input_data.get("VPCDatabaseEndpointService")
        vpc_service_webserver = input_data.get("VPCWebserverEndpointService")
        subnet_ids = input_data.get("SubnetIds")
        security_group_id = input_data.get("SecurityGroupId")
        tags = input_data.get("Tags")

        if request_type in ["Create", "Update"]:
            if log_group_arns and request_type == "Create":
                for log_group_arn in log_group_arns:
                    logger.info("Tagging log group: %s", log_group_arn)
                    tag_log_group(log_group_arn, tags)

            create_vpc_endpoint(vpc_service_database, vpc_id, subnet_ids, security_group_id, tags)

            vpc_endpoint_id = create_vpc_endpoint(vpc_service_webserver, vpc_id, subnet_ids, security_group_id, tags)
            logger.info("Getting ip addresses from webserver service: %s", vpc_service_webserver)
            ip_addresses = get_ips_from_endpoint(vpc_endpoint_id)

            result = {
                "ipAddress1": ip_addresses[0],
                "ipAddress2": ip_addresses[1]
                }
            _cfnresponse.send(event, context, _cfnresponse.SUCCESS, result, resource_id)

        if request_type == "Delete":
            logger.info("Deleting resources")
            delete_vpc_endpoints(vpc_id, vpc_service_database, vpc_service_webserver)

            _cfnresponse.send(event, context, _cfnresponse.SUCCESS, {}, resource_id)
    except Exception as e:
        logger.error(e)
        _cfnresponse.send(event, context, _cfnresponse.FAILED, {"Message": str(e)}, resource_id)
