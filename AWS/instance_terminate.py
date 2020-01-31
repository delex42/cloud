#! /usr/bin/python3

from aws_utils import *

def main():    
    profile = input("--> Profile: ")
    aws = AwsUtils(profile)

    instance_id = input("--> Instance ID: ")
    aws.instance_terminate(instance_id)

if __name__ == "__main__":
    main()
