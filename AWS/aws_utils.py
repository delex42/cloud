#! /usr/bin/python3

import boto3, json
from dateutil import parser

class AwsUtils:
    def __init__(self, profile):
        self.profile = profile
        if profile != "none":
            self.session = boto3.Session(profile_name=profile)
            self.ec2_resource = self.session.resource('ec2')
            self.ec2_client = self.session.client('ec2')
        # List of instance IDs that we know about. No point in keeping the
        # entire instance objects, better to fetch the object every time.
        self.instance_id_list = []

    def dump(self, obj):
        for attr in dir(obj):
            print("obj.%s = %r" % (attr, getattr(obj, attr)))
        
    def print_json(self, json_object):
        print(json.dumps(json_object, indent=4, sort_keys=True, default=str))

    ### Helper functions
    def _build_vpc_filter(self, vpc):
        filter = [
            {
                'Name': 'vpc-id',
                'Values': [ vpc ]
            }
        ]
        return filter
        
    ### AMIs
    def ami_get_latest(self):
        filters = [ {
            'Name': 'name',
            'Values': ['amzn-ami-hvm-*']
        },{
            'Name': 'description',
            'Values': ['Amazon Linux AMI*']
        },{
            'Name': 'architecture',
            'Values': ['x86_64']
        },{
            'Name': 'owner-alias',
            'Values': ['amazon']
        },{
            'Name': 'owner-id',
            'Values': ['137112412989']
        },{
            'Name': 'state',
            'Values': ['available']
        },{
            'Name': 'root-device-type',
            'Values': ['ebs']
        },{
            'Name': 'virtualization-type',
            'Values': ['hvm']
        },{
            'Name': 'hypervisor',
            'Values': ['xen']
        },{
            'Name': 'image-type',
            'Values': ['machine']
        } ]

        resp = self.ec2_client.describe_images(Owners=['amazon'], Filters=filters)
        latest = None
        for image in resp['Images']:
            if not latest:
                latest = image
                continue
            if parser.parse(image['CreationDate']) > parser.parse(latest['CreationDate']):
                latest = image
        ami = latest['ImageId']
        print('Found latest Amazon Linux AMI ' + ami)
        return ami

    ### Profiles
    def profile_print(self):
        print(self.profile)

    def profile_list_available(self):
        self.print_json(boto3.Session().available_profiles)
        
    ### Instances
    def instance_display(self, instance_id, display_type=''):
        i = self.ec2_resource.Instance(instance_id)
        if display_type == 'Full':
            self.dump(i)
            return
        if display_type == 'Network':
            print(i.network_interfaces_attribute)
            return

    def instance_display_all(self):
        for instance_id in self.instance_id_list:
            self.instance_display(instance_id, display_type='Full')

    def instance_get_name(self, instance_id):
        i = self.ec2_resource.Instance(instance_id)
        name = ''
        if i.tags:
            for tags in i.tags:
                if tags['Key'] == 'Name':
                    name = tags['Value']
        return name
            
    # Lists all instances in that account / region
    def instance_list(self, display_type='Full'):
        resp = self.ec2_client.describe_instances()
        if display_type == 'Full':
            self.print_json(resp)
            return
        for r in resp['Reservations']:
            for i in r['Instances']:
                instance_id = i['InstanceId']
                print('***** ' + instance_id)
                print('Name: ' + self.instance_get_name(instance_id))
                print('State: ' + i['State']['Name'])
                if display_type == 'Network':
                    if 'VpcId' in i:
                        vpc_id = i['VpcId']
                        vpc_name = self.vpc_get_name_from_id(vpc_id)
                        print('VPC: ' + vpc_name)
                    if 'PrivateIpAddress' in i:
                        print('PrivateIpAddress: ' + i['PrivateIpAddress'])
                    if 'PublicIpAddress' in i:
                        print('PublicIpAddress: ' + i['PublicIpAddress'])
                    print()

    def instance_list_for_all_profiles(self, display_type='Full'):
        for profile in boto3.Session().available_profiles:
            print('------------------ ' + profile + ' ------------------')
            AwsUtils(profile).instance_list(display_type)

    def instance_terminate(self, instance_id):
        resp = self.ec2_resource.Instance(instance_id).terminate()
        self.print_json(resp)
            
    def instance_wait_until_running(self, instance_id, display_type=''):
        i = self.ec2_resource.Instance(instance_id)
        print('Waiting for instance ' + instance_id + '... ')
        i.wait_until_running()
        print('Done')
        self.instance_display(instance_id, display_type)

    def instance_wait_until_running_all(self, display_type=''):
        for instance_id in self.instance_id_list:
            self.instance_wait_until_running(instance_id, display_type)

    def instance_tag_add(self, instance_id, tag_key, tag_value):
        # i = self.ec2_resource.Instance(instance_id)
        self.ec2_client.create_tags(Resources=[instance_id],
                                    Tags=[
                                        {'Key': tag_key,
                                         'Value': tag_value
                                        }
                                    ])

    def instance_create(self,
                        name,
                        subnet,
                        sg,
                        instance_type='t2.micro',
                        associate_public_ip=True,
                        display=False):
        instances = self.ec2_resource.create_instances(
            ImageId=self.ami_get_latest(),
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            KeyName=self.profile,  # my key pairs always have the same name as profile
            NetworkInterfaces=[
                {
                    'DeviceIndex': 0,
                    'SubnetId': subnet,
                    'AssociatePublicIpAddress': associate_public_ip,
                    'Groups': [ sg ]
                }
            ]
            # SubnetId=subnet
        )
        for instance in instances:
            self.instance_tag_add(instance.id, 'Name', name)            
            self.instance_id_list.append(instance.id)
            print('Created instance ' + instance.id)
            if display:
                self.dump(instance)
        
    ### VPCs
    def vpc_get_name_from_id(self, identifier):
        resp = self.ec2_client.describe_vpcs(
            VpcIds=[
                identifier,
            ]
        )
        for tag in resp['Vpcs'][0]['Tags']:
            if tag['Key'] == 'Name':
                return(tag['Value'])
    
    def vpc_get_all(self, display=False):
        vpcs = self.ec2_client.describe_vpcs()
        if display:
            print("***** VPCs *****")
            self.print_json(vpcs['Vpcs'])
        return vpcs

    ### Subnets
    def subnet_get_all(self, vpc = '', display=False):
        if vpc == '':
            subnets = self.ec2_client.describe_subnets()
        else:
            filters = self._build_vpc_filter(vpc)
            subnets = self.ec2_client.describe_subnets(
                Filters = filters)
        if display:
            print("***** Subnets *****")
            self.print_json(subnets['Subnets'])
        return subnets

    ### Security Groups
    def sg_get_all(self, vpc = '', display=False):
        if vpc == '':
            sgs = self.ec2_client.describe_security_groups()
        else:
            filters = self._build_vpc_filter(vpc)
            sgs = self.ec2_client.describe_security_groups(
                Filters = filters)
        if display:
            print("***** Security Groups *****")
            self.print_json(sgs['SecurityGroups'])
        return sgs
