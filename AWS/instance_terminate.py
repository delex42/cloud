#! /usr/bin/python3

from aws_utils import *

def main():
    while True:
        profile = input("Profile: ")
        aws = AwsUtils(profile)

        aws.instance_list(display_type='Network')

        total = input("How many instances to terminate: ")
        for i in range(int(total)):
            instance_id = input("Instance ID: ")
            aws.instance_terminate(instance_id)

if __name__ == "__main__":
    main()

