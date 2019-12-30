#! /usr/bin/python3

import boto3

while True:
    profile = input("Profile: ")
    subnet = input("Subnet: ")
    sg = input("Security group: ")

    session = boto3.Session(profile_name=profile)

    ec2 = session.resource('ec2')

    # create a new EC2 instance
    instance = ec2.create_instances(
        ImageId='ami-00eb20669e0990cb4',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=profile,  # my key pairs always have the same name as profile
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'SubnetId': subnet,
                'AssociatePublicIpAddress': True,
                'Groups': [ sg ]
            }
        ]
        # SubnetId=subnet
    )

    print(instance)

