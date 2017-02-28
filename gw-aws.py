#!/Users/dland/virtualenv/netaddr/bin/python
from netaddr import IPNetwork
from optparse import OptionParser
import sys
import json
import os
import re
import boto3
import copy
from bottle import Bottle, response, request, abort

app = Bottle()

listenaddr = os.environ.get('listenaddr', '0.0.0.0')
listenport = os.environ.get('listenport', '8090')
bug = bool(os.environ.get('debug', False))

class AutoVivification(dict):
	'''Implementation of perl's autovivification feature'''
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

def get_aws_subnets():
    '''Get AWS info for vpc and vpc subnets and pack them into a dictionary'''
    ec2c = boto3.client('ec2')
    regions = ec2c.describe_regions()
    data = AutoVivification()
    for region in regions['Regions']:
        ec2 = boto3.resource('ec2', region_name=region['RegionName'])
        vpcs = ec2.vpcs.all()
        for vpc in vpcs:
            nvpc = ec2.Vpc(vpc.id)
            subnet_iterator = nvpc.subnets.all()
            for subnet in subnet_iterator:
                    hastags = False
                    alltags = "TAGS="
                    if subnet.tags:
                        hastags = True
                        for tag in subnet.tags:
                            alltags += "%s:%s," % (tag['Key'], tag['Value'])
                    if hastags:
                            data[vpc.cidr_block][subnet.cidr_block] = alltags
                    else:
                        if subnet.cidr_block not in data.get(vpc.cidr_block, {}):
                            data[vpc.cidr_block][subnet.cidr_block] = "unset"
    return data


def get_used_ips(subnets):
    '''Take a list of subnets and return a list of ips in those subnets'''
    x = []
    for cidr in subnets:
        ip = IPNetwork(cidr)
        x += list(ip)
    return sorted(x)

def next_available(entity):
  '''get the next free subnet in a cidr'''
  retranges = []
  # get all the used ranges via AWS api
  awsnets = get_aws_subnets()
  awslist = awsnets[entity['vpc']].keys()
  used = get_used_ips(awslist)
  # if customcidr is set, use only that as the range we're comparing
  if entity['customcidr']:
      subnets = [IPNetwork(entity['customcidr'])]
  # otherwise, calculate all the subnets in the cidr we want space in by prefix
  else:
      ss = IPNetwork(entity['vpc'])
      subnets = list(ss.subnet(int(entity['prefix'])))
  # get 'range' number of free subnets
  for i in range(0,int(entity['ranges'])):
    # start out having not found anything
    found = False
    for s in subnets:
        ips = IPNetwork(s)
        subnet = list(ips)
        if set(used).isdisjoint(subnet):
            if bug:
                print("## %s not used!!!!!!!!!!" % str(s))
            found = str(s)
            break
    # we put found down here because if we go through all the subnets and we still haven't found something
    # we have a problem
    if found:
      used += get_used_ips([found])
      retranges.append(found)
      if bug:
            print("Use: %s" % found)
    else:
      if entity['customcidr']:
          abort(500, "ERROR: cidr not available")
      else:
         abort(500, "ERROR: we might we out of ranges?")
  # return json.dumps(retranges)
  return retranges

if bug:
    print("listenaddr: %s" % listenaddr)
    print("listenport: %s" % listenport)

@app.route('/')
def cidr_info():
    response.content_type = 'application/json'
    try:
        data = get_aws_subnets()
        return json.dumps(data)
    except:
        abort(500, "ERROR: issue retrieving network information from AWS")

@app.post('/')
def cidr_get():
    response.content_type = 'application/json'
    data = request.body.readline()
    if data:
        entity = json.loads(data)
    else:
        entity = {}

    if 'ranges' not in entity:
        entity['ranges'] = 1

    if 'prefix' not in entity:
        entity['prefix'] = 25

    if 'customcidr' not in entity:
        entity['customcidr'] = None

    if 'vpc' not in entity:
        abort(500, "ERROR: you must provide a vpc")

    return json.dumps(next_available(entity))

if __name__ == '__main__':
    try:
        app.run(host=listenaddr, port=listenport, server='tornado', debug=bug)
    except KeyboardInterrupt:
        sys.exit("Aborted by Ctrl-C!")
