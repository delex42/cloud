#! /usr/bin/python3

from aws_utils import *

def main():    
    while True:
        AwsUtils('none').instance_list_for_all_profiles('Network')

        profile = input("--> Profile: ")
        aws = AwsUtils(profile)

        instance_id = input("--> Instance ID: ")
        aws.instance_terminate(instance_id)

if __name__ == "__main__":
    main()
