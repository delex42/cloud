#! /usr/bin/python3

from aws_utils import *

def main():
    total = input("How many instances to create: ")
    aws_list = []
    
    for i in range(int(total)):
        AwsUtils('none').profile_list_available()
        profile = input("Profile: ")
        aws = AwsUtils(profile)

        name = input("Instance name: ")

        # List VPCs in that account / region and ask user to choose one
        aws.vpc_get_all(True)
        vpc = input("VPC: ")
        # Set the VPC in the utils object to automatically filter on that VPC from now on
        
        # List subnets in that VPC, and ask user to choose one
        aws.subnet_get_all(vpc, True)
        subnet = input("Subnet: ")

        # List security groups in that VPC, and ask user to choose one
        aws.sg_get_all(vpc, True)
        sg = input("Security group: ")

        aws.instance_create(name = name, subnet=subnet, sg=sg)
        aws_list.append(aws)

        # aws.instance_display_all()
        
    for aws in aws_list:
        aws.profile_print()
        aws.instance_wait_until_running_all(display_type='Network')
        print()

if __name__ == "__main__":
    main()
