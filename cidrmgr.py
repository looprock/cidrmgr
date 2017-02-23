#!/Users/dland/virtualenv/netaddr/bin/python
from netaddr import IPNetwork
import etcd
from optparse import OptionParser
import sys
import json
from bottle import Bottle, response, request, abort

app = Bottle()

configpath = "/config"

etcdsrv = "localhost"

debug = True

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

client = etcd.Client(host=etcdsrv, port=2379)

if debug:
    print(client.leader)

@app.delete('/cidr/:s/:b')
def cidr_delete(s,b):
    response.content_type = 'application/json'
    try:
        cstring = "%s/%s" % (s,b)
        cidrpath = "%s/%s" % (configpath, cstring.replace('/', '_'))
        print('deleting cidrpath: %s' % cidrpath)
        client.delete(cidrpath)
        return json.dumps({'status': 'ok'})
    except:
        abort(500, "error deleteing from cidr store")

@app.get('/cidr')
def cidr_list():
    response.content_type = 'application/json'
    try:
        cdirs = []
        r = client.read(configpath, recursive=True, sorted=True)
        for child in r.children:
            cidr = child.key.split("/")[-1].replace('_', '/')
            cdirs.append(cidr)
        return json.dumps(cdirs)
    except:
        abort(500, "error listing cidr store")


@app.post('/cidr')
def cidr_get():
    response.content_type = 'application/json'
    data = request.body.readline()
    if data:
        entity = json.loads(data)
    else:
        entity = {}

    if 'numberranges' not in entity:
        numberranges = 1
    else:
        numberranges = int(entity['numberranges'])

    if 'bitrange' not in entity:
        bitrange = 16
    else:
        bitrange = int(entity['bitrange'])

    # abort(400, "Error adding new check!")
    retranges = []
    for i in range(0,numberranges):
        x = []
        twentyfour = []
        found = False
        customcidr = False
        testranges = []
        try:
            r = client.read(configpath, recursive=True, sorted=True)
            for child in r.children:
                cidr = child.key.split("/")[-1].replace('_', '/')
                if debug:
                    print("adding %s (%s) to x" % (cidr, child.value))
                ip = IPNetwork(cidr)
                x += list(ip)
                x = sorted(x)
                if int(str(x[-1]).split('.')[2]) < 255:
                    twentyfour.append(cidr)
        except etcd.EtcdKeyNotFound:
            abort(500, "error reading cidrs")

        if debug:
            print("length of x: %d" % len(x))

        if 'customcidr' in entity:
            if debug:
                print("detected custom cidr: %s" % entity['customcidr'])
            testranges.append(entity['customcidr'])
            customcidr = True
        else:
            # for i in range(0,256):
            #    testranges.append("10.%d.0.0/%d" % (i, bitrange))
            # first add the supernets of the /16 subnets which possibly aren't full
            if bitrange == 24:
                if twentyfour:
                    tmpsupers = []
                    for i in twentyfour:
                        tfip = IPNetwork(i)
                        sn = tfip.supernet(16)
                        tmpsupers.append(str(sn[0]))
                    for i in uniqify(tmpsupers):
                        for dot in range(0,256):
                            t = i.split('.')
                            tfsub = "%s.%s.%d.0/24" % (t[0],t[1],dot)
                            testranges.append(tfsub)
            # last we add the generic /16 list
            for i in range(16,31):
                testranges.append("172.%d.0.0/%d" % (i, bitrange))

        for i in testranges:
            if not found:
                if debug:
                    print("testing: %s" % i)
                ip = IPNetwork(i)
                y = list(ip)

                if debug:
                    print("length of y: %d" % len(y))
                    print("checking for shared values across x and y")
                # if not any(i in x for i in y):
                if set(x).isdisjoint(y):
                    found = i

        if found:
            retranges.append(found)
            print("Use: %s" % found)
            cidrpath = "%s/%s" % (configpath, found.replace('/', '_'))
            if debug:
                print("writing: %s" % cidrpath)
            client.write(cidrpath, "cluster identifier goes here")
        else:
            if customcidr:
                abort(500, "Error: cidr not available")
            else:
                abort(500, "Error: we might we out of ranges?")
    return json.dumps(retranges)

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port='8080')
    except KeyboardInterrupt:
        sys.exit("Aborted by Ctrl-C!")
