#! /usr/bin/python3

from aws_utils import *

import argparse

def main():    
    # profile = input("--> Profile: ")

    parser = argparse.ArgumentParser(description='parser')
    parser.add_argument("--p")

    args = parser.parse_args()
    profile = args.p
    print(profile)
    
    aws = AwsUtils(profile)

    while True:
        instance_id = input("--> Instance ID: ")
        aws.instance_terminate(instance_id)

if __name__ == "__main__":
    main()
