#! /usr/bin/python3

from aws_utils import *

def main():
    total = input("How many instances to create: ")
    aws_list = []
    
    for i in range(int(total)):
        profile = input("Profile: ")
        aws = AwsUtils(profile)

        name = input("Name: ")
        ami = input("AMI: ")
        if ami == '':
            ami = 'ami-00eb20669e0990cb4'
        
        # List subnets and ask user to choose one
        aws.subnet_get_all(True)
        subnet = input("Subnet: ")

        # List security groups and ask user to choose one
        aws.sg_get_all(True)
        sg = input("Security group: ")

        aws.instance_create(name = name, image_id = ami, subnet=subnet, sg=sg)
        aws_list.append(aws)

        # aws.instance_display_all()
        
    for aws in aws_list:
        aws.profile_print()
        aws.instance_wait_until_running_all(display_type='Network')
        print()

if __name__ == "__main__":
    main()
