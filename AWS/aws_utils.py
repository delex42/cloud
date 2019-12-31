#! /usr/bin/python3

import boto3, json

class AwsUtils:
    def __init__(self, profile):
        self.profile = profile
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


    ### Profiles
    def profile_print(self):
        print(self.profile)

    def profile_list_available(self):
        self.print_json(self.session.available_profiles)

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

    # Lists all instances in that account / region
    def instance_list(self, display_type='Full'):
        resp = self.ec2_client.describe_instances()
        if display_type == 'Full':
            self.print_json(resp)
            return
        for r in resp['Reservations']:
            for i in r['Instances']:
                print('***** ' + i['InstanceId'])
                print('State: ' + i['State']['Name'])
                if display_type == 'Network':
                    if 'PrivateIpAddress' in i:
                        print('PrivateIpAddress: ' + i['PrivateIpAddress'])
                    if 'PublicIpAddress' in i:
                        print('PublicIpAddress: ' + i['PublicIpAddress'])
                    print()

    def instance_terminate(self, instance_id):
        resp = self.ec2_resource.Instance(instance_id).stop()
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

    def instance_create(self,
                        subnet,
                        sg,
                        image_id='ami-00eb20669e0990cb4',
                        instance_type='t2.micro',
                        associate_public_ip=True,
                        display=False):
        instances = self.ec2_resource.create_instances(
            ImageId=image_id,
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
            self.instance_id_list.append(instance.id)
            print('Created instance ' + instance.id)
            if display:
                self.dump(instance)

    ### VPCs
    def vpc_get_all(self, display=False):
        vpcs = self.ec2_client.describe_vpcs()
        if display:
            print("***** VPCs *****")
            self.print_json(vpcs['Vpcs'])
        return vpcs

    ### Subnets
    def subnet_get_all(self, display=False):
        subnets = self.ec2_client.describe_subnets()
        if display:
            print("***** Subnets *****")
            self.print_json(subnets['Subnets'])
        return subnets

    ### Security Groups
    def sg_get_all(self, display=False):
        sgs = self.ec2_client.describe_security_groups()
        if display:
            print("***** Security Groups *****")
            self.print_json(sgs['SecurityGroups'])
        return sgs

