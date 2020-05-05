#! /usr/bin/python

import requests, json, urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONTROLLER = "13.52.171.86"
OLDER_AMIS = {
    'hvm-cloudx-aws-011519',
    'hvm-cloudx-aws-041519',
    'hvm-cloudx-aws-071519',
    'hvm-cloudx-aws-093019'}

def print_json(json_object):
    print(json.dumps(json_object, indent=4, sort_keys=True, default=str))

# login and store CID
def login(controller):
    url = "https://" + controller + "/v1/api"

    payload = {'action': 'login',
               'username': 'admin',
               'password': 'password'}

    response = requests.request("POST", url, headers={}, data = payload, files = [], verify = False).text.encode('utf8')
    
    r = json.loads(response)
    # print(r['CID'])
    return r['CID']

# get all gateways
def get_all_gateways(controller, cid):
    url = "https://" + controller + "/v1/api?action=list_vpcs_summary&CID=" + cid + "&acx_gw_only=no"
    response = requests.request("GET", url, headers={}, data = {}, verify = False).text.encode('utf8')
    r = json.loads(response)
    # print_json(r)
    return r

def list_gateways_with_older_amis(controller, cid, gateways):
    # iterate on every gateway name, get its image name, compare with the list of older AMIs
    for gateway in gateways['results']:
        name = gateway['cloudn_gateway_inst_name']
        # print(name)
        url = "https://" + controller + "/v1/api?action=get_gateway_info&&CID=" + cid + "&gateway_name=" + name
        response = requests.request("GET", url, headers={}, data = {}, verify = False).text.encode('utf8')
        r = json.loads(response)
        # print_json(r)
        if 'results' in r:
            ami = r['results']['gw_image_name']
            print 'Gateway = ' + name + ', AMI = ' + ami,
            if ami in OLDER_AMIS:
                print('--> OLDER AMI')
            else:
                print('--> AMI is fine')
                
def main():
    cid = login(CONTROLLER)
    gateways = get_all_gateways(CONTROLLER, cid)
    list_gateways_with_older_amis(CONTROLLER, cid, gateways)

if __name__ == "__main__":
    main()
