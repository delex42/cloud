#! /usr/bin/python3

from aws_utils import *

def main():
    total = input("How many instances to create: ")
    aws_list = []
    
    for i in range(int(total)):
        AwsUtils('none').profile_list_available()
        profile = input("Profile: ")
        aws = AwsUtils(profile)

        # Existing instances in that profile
        print("Existing instances in that profile:")
        aws.instance_list('Network')
        
        # Ask for one instance, or private+public
        bastion = input("Bastion pair (y/n): ")
        if bastion == 'y':
            bastion = True
            name_bastion = input("Bastion name: ")
            name_private = input("Private name: ")
        else:
            name = input("Instance name: ")

        # List VPCs in that account / region and ask user to choose one
        aws.vpc_get_all(True)
        vpc = input("VPC: ")
        # Set the VPC in the utils object to automatically filter on that VPC from now on
        
        # List subnets in that VPC, and ask user to choose one
        aws.subnet_get_all(vpc, True)
        if bastion is True:
            subnet_bastion = input("Bastion subnet: ")
            subnet_private = input("Private subnet: ")
        else:
            subnet = input("Subnet: ")

        # List security groups in that VPC, and ask user to choose one
        aws.sg_get_all(vpc, True)
        sg = input("Security group: ")

        if bastion is True:
            aws.instance_create(name = name_bastion,
                                subnet = subnet_bastion,
                                sg=sg,
                                associate_public_ip = True)
            aws.instance_create(name = name_private,
                                subnet = subnet_private,
                                sg=sg,
                                associate_public_ip = False)
        else:            
            # Ask for public IP association
            public_ip = input("Associate public IP (y/n): ")
            if public_ip == 'y':
                associate_public_ip = True
            else:
                associate_public_ip = False                
                aws.instance_create(name = name,
                                    subnet = subnet,
                                    sg = sg,
                                    associate_public_ip = associate_public_ip)
        
        aws_list.append(aws)

        # aws.instance_display_all()
        
    for aws in aws_list:
        aws.profile_print()
        aws.instance_wait_until_running_all(display_type='Network')
        print()

if __name__ == "__main__":
    main()
