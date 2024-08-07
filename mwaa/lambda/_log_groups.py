"""
This module provides functions for interacting Cloud Watch Log Groups
"""

import boto3

def tag_log_group(log_group_arn, tags):
    "A function to tal log groups"
    log_group_name = log_group_arn.split(":log-group:")[1].split(":*")[0]
    client = boto3.client("logs")
    client.tag_log_group(
        logGroupName=log_group_name,
        tags=tags
    )
