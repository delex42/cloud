#! /usr/bin/python3

from aws_utils import *

def main():
    AwsUtils('none').instance_list_for_all_profiles('Network')

if __name__ == "__main__":
    main()
