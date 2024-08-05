"""
This module provides functions for interacting with VPC Endpoints
"""

from time import sleep
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class UnexpectedNumberOfIpAddressesError(Exception):
    "A custom exception for unexpected number of ip addresses found"

def vpc_endpoint_exists(vpc_id, service_name):
    "A function to check whether a give VPC endpoint exists already"
    ec2_client = boto3.client("ec2")
    ec2_response = ec2_client.describe_vpc_endpoints(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "service-name", "Values": [service_name]}
        ]
    )
    if len(ec2_response["VpcEndpoints"]) > 0:
        return ec2_response["VpcEndpoints"][0]["VpcEndpointId"]
    return None

def create_vpc_endpoint(service_name, vpc_id, subnet_ids, security_group_id, tags):
    "A function to create VPC endpoint for endpoint service name in AWS service account"
    vpc_endpoint_id = vpc_endpoint_exists(vpc_id, service_name)
    if vpc_endpoint_id is not None:
        logger.info("VPC endpoint for service %s exists already - %s", service_name, vpc_endpoint_id)
        return vpc_endpoint_id
    logger.info("Creating VPC Endpoint for service: %s", service_name)
    ec2_client = boto3.client("ec2")
    ec2_response = ec2_client.create_vpc_endpoint(
        VpcEndpointType="Interface",
        VpcId=vpc_id,
        ServiceName=service_name,
        SubnetIds=subnet_ids,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[{
            "ResourceType": "vpc-endpoint",
            "Tags": [{"Key": k, "Value": v} for k, v in tags.items()] + [{"Key": "MWAACustomerManaged", "Value": "true"}]
        }]
    )
    logger.info("Vpc endpoint for service %s created successfully", service_name)
    return ec2_response.get("VpcEndpoint").get("VpcEndpointId")

def get_ips_from_endpoint(vpc_endpoint_id):
    "A function to extract IP addresses from network interfaces attached to VPC endpoint"
    ec2_client = boto3.client("ec2")
    vpc_state = None
    while vpc_state != "available":
        logger.info("Checking if webserver endpoint is available")
        ec2_response = ec2_client.describe_vpc_endpoints(Filters=[{"Name": "vpc-endpoint-id","Values":[vpc_endpoint_id]}])
        vpc_state = ec2_response["VpcEndpoints"][0]["State"]
        if vpc_state != "available":
            sleep(3)
            logger.info("Waiting 3s before checking again")

    network_interface_ids = ec2_response["VpcEndpoints"][0]["NetworkInterfaceIds"]

    ec2_response = ec2_client.describe_network_interfaces(
            NetworkInterfaceIds=network_interface_ids)
    ip_addresses = []
    network_interfaces = ec2_response["NetworkInterfaces"]
    for ni in network_interfaces:
        ip_addresses.append(ni["PrivateIpAddress"])

    if len(ip_addresses) != 2:
        logger.error("Found an unexpected number of ip addresses attached to the vpc endpoint: %s", ip_addresses)
        raise UnexpectedNumberOfIpAddressesError("There should be 2 Ip addresses attached to the vpc endpoint")
    return ip_addresses

def delete_vpc_endpoints(vpc_id, vpc_service_database, vpc_service_webserver):
    "A function to delete existing VPC endpoints attached to MWAA"
    endpoints_to_delete = []
    if vpc_service_database:
        vpc_endpoint_id = vpc_endpoint_exists(vpc_id, vpc_service_database)
        if vpc_endpoint_id is not None:
            endpoints_to_delete.append(vpc_endpoint_id)

    if vpc_service_webserver:
        vpc_endpoint_id = vpc_endpoint_exists(vpc_id, vpc_service_webserver)
        if vpc_endpoint_id is not None:
            endpoints_to_delete.append(vpc_endpoint_id)

    if endpoints_to_delete:
        logger.info("Deleting endpoints %s", endpoints_to_delete)
        ec2_client = boto3.client("ec2")
        ec2_client.delete_vpc_endpoints(
            DryRun=False,
            VpcEndpointIds=endpoints_to_delete
        )
    else:
        logger.info("No VPC endpoints to delete")
