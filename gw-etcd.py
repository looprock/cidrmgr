#!/Users/dland/virtualenv/netaddr/bin/python
from netaddr import IPNetwork
import etcd
from optparse import OptionParser
import sys
import json
import os
import re
import boto3
from bottle import Bottle, response, request, abort

app = Bottle()

bug = bool(os.environ.get('debug', 'false'))
etcdpath = os.environ.get('etcdpath', '/config')
etcdaddr = os.environ.get('etcdaddr', 'localhost')
etcdport = int(os.environ.get('etcdport', '2379'))
listenaddr = os.environ.get('listenaddr', '0.0.0.0')
listenport = os.environ.get('listenport', '8090')

# NO! bad answer, we need this to be dynamic and/or passed in..
# which means I also need to fix the empty range thing..

# TODO:
# fix readme
# and also how to wire together different VPCs...

def uniqify(seq, idfun=None):
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def munge(string):
    underscore = re.search("_", string)
    if underscore:
        x = string.replace('_', '/')
    else:
        x = string.replace('/', '_')
    return x

def get_aws_subnets():
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


def get_used(superset):
    try:
        cidrpath = "%s/%s" % (etcdpath, munge(superset))
        r = client.read(cidrpath, recursive=True, sorted=True)
        x = []
        for child in r.children:
            if not child.value:
                break
            else:
                print(child.key)
                cidr = munge(child.key.split("/")[-1])
                if bug:
                    print("adding %s (%s) to x" % (cidr, child.value))
                ip = IPNetwork(cidr)
                x += list(ip)
        return sorted(x)
    except etcd.EtcdKeyNotFound:
        return []

def next_available(entity):
  retranges = []
  for i in range(0,int(entity['ranges'])):
    found = False
    if entity['customcidr']:
        subnets = [IPNetwork(entity['customcidr'])]
    else:
        ss = IPNetwork(entity['vpc'])
        subnets = list(ss.subnet(int(entity['prefix'])))
    if bug:
        print(subnets)
    for s in subnets:
        if not found:
            used = None
            used = get_used(entity['vpc'])
            if bug:
                print("testing: %s" % s)
            ips = IPNetwork(s)
            subnet = list(ips)
            if bug:
                # print(subnet)
                print("length of subnet: %d" % len(subnet))
                print("checking for shared values across %s and %s" % (str(entity['vpc']), str(s)))
            if set(used).isdisjoint(subnet):
                if bug:
                    print("********* MATCH!!!!!!!!!!")
                found = str(s)
    if found:
      retranges.append(found)
      if bug:
          print("Use: %s" % found)
      cidrpath = "%s/%s/%s" % (etcdpath, munge(entity['vpc']), munge(str(found)))
      if bug:
          print("writing: %s" % cidrpath)
      client.write(cidrpath, entity['comment'])
    else:
      if entity['customcidr']:
          abort(500, "ERROR: cidr not available")
      else:
         abort(500, "ERROR: we might we out of ranges?")
  # return json.dumps(retranges)
  return retranges


# generate nested python dictionaries, copied from here:
# http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
class AutoVivification(dict):
	"""Implementation of perl's autovivification feature."""
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

client = etcd.Client(host=etcdaddr, port=etcdport)

if bug:
    print(client.leader)
    print("etcdpath: %s" % etcdpath)
    print("etcdaddr: %s" % etcdaddr)
    print("etcdport: %d" % etcdport)
    print("listenaddr: %s" % listenaddr)
    print("listenport: %s" % listenport)

@app.delete('/:ssone/:sstwo/:s/:b')
def cidr_delete(ssone, sstwo, s,b):
    response.content_type = 'application/json'
    try:
        cidrpath = "%s/%s_%s/%s_%s" % (etcdpath, ssone, sstwo, s, b)
        print('deleting cidrpath: %s' % cidrpath)
        client.delete(cidrpath)
        return json.dumps({'status': 'ok'})
    except:
        abort(500, "ERROR: unable to delete from cidr store")

@app.route('/')
@app.route('/<s>/<b>')
def cidr_info(s=None,b=None):
    response.content_type = 'application/json'
    try:
        data = AutoVivification()
        cstring = None
        if s:
            if not b:
                abort(500, "ERROR: you must provide the bit range!")
            else:
                cstring = "%s/%s" % (s,b)
        if bug:
            print("DEBUG: reading from: %s" % etcdpath)
        r = client.read(etcdpath, recursive=True, sorted=True)
        for child in r.children:
            print(child.key.split("/"))
            data[munge(child.key.split('/')[4])][munge(child.key.split('/')[5])] = child.value
            # cidr = munge(child.key.split("/")[-1])
            # data[cidr] = child.value
        if cstring:
            return json.dumps(data[cstring])
        else:
            return json.dumps(data)
    except:
        abort(500, "ERROR: issue retrieving cidr store")

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

    if 'comment' not in entity:
        abort(500, "ERROR: you must provide a comment")

    if 'vpc' not in entity:
        abort(500, "ERROR: you must provide a vpc")

    return json.dumps(next_available(entity))

if __name__ == '__main__':
    try:
        app.run(host=listenaddr, port=listenport, server='tornado', debug=bug)
    except KeyboardInterrupt:
        sys.exit("Aborted by Ctrl-C!")
