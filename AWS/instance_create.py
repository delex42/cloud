#! /usr/bin/python3

import boto3, aws_utils
from aws_utils import *

def main():
    total = input("How many instances to create: ")
    aws_list = []

    for i in range(int(total)):
        profile = input("Profile: ")
        aws = AwsUtils(profile)

        # List subnets and ask user to choose one
        aws.subnet_get_all(True)
        subnet = input("Subnet: ")

        # List security groups and ask user to choose one
        aws.sg_get_all(True)
        sg = input("Security group: ")

        aws.instance_create(subnet=subnet, sg=sg)
        aws_list.append(aws)

        # aws.instance_display_all()

    for aws in aws_list:
        aws.print_profile()
        aws.instance_wait_until_running_all(display_type='Network')
        print()

if __name__ == "__main__":
    main()

