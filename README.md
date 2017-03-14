# cidrmgr
a restful API for tracking CIDRs, backed in etcd

# Usage

## AWS backend

The AWS backend only supports:

1. querying the exising vpc/cidr spaces

2. finding the next avialable subnet

### Staring the service

#### Environment Variables

debug - debug mode - default: 'false'

listenaddr - IP to listen on  - default: '0.0.0.0'

listenport - port to listen on - default: '8090'

AWS_ACCESS_KEY_ID - access key to query AWS API

AWS_SECRET_ACCESS_KEY - secret key to query AWS API

AWS_DEFAULT_REGION - default region for AWS API to use

#### Example

listenaddr='127.0.0.1' debug='true' ./gw-aws.py

### Querying the service

#### get the current subnets

```
ip-10-1-1-159:~ dland$ http localhost:8090
HTTP/1.1 200 OK
Content-Length: 1884
Content-Type: application/json
Server: TornadoServer/4.4.2

{
    "172.31.0.0/16": {
        "172.31.0.0/20": "TAGS=Name:public-east-1d,",
        "172.31.32.0/20": "TAGS=Name:public-east-1e,",
        "172.31.65.0/24": "TAGS=Name:internal-az2,",
        "172.31.68.0/22": "TAGS=Name:public-east-1c,"
    }
}
```

#### get the next available range(s)

##### options

vpc - VPC CIDR subnet to check in - required

ranges  - (integer) number of ranges you want - default: 1

prefix - (integer) the prefix of the range(s) you want - default: 25

customcidr - you can use this to test if a CIDR is available. If it is you'll get a 200, otherwise it's in use


##### Examples

###### get the next /25

```
ip-10-1-1-159:~ dland$ http POST http://localhost:8090 vpc=172.31.0.0/16
HTTP/1.1 200 OK
Content-Length: 18
Content-Type: application/json
Server: TornadoServer/4.4.2

[
    "172.31.64.0/25"
]
```

###### get two /24 subnets

```
ip-10-1-1-159:~ dland$ http --timeout 600 POST http://localhost:8090 vpc=172.31.0.0/16 ranges='2' prefix='24'
HTTP/1.1 200 OK
Content-Length: 36
Content-Type: application/json
Server: TornadoServer/4.4.2

[
    "172.31.64.0/24",
    "172.31.66.0/24"
]
```

## ETCD backend

If you're using etcd as your backend, you must first seed the initial entry:

etcdctl set <your_etcdpath_here>/172.31.0.0_16 "default vpc cidr"

### Starting the services

#### Environment Variables

debug - debug mode - default: 'false'

listenaddr - IP to listen on  - default: '0.0.0.0'

listenport - port to listen on - default: '8090'

etcdaddr - etcd server - default: 'localhost'

etcdport - etcd port - default: '2379'

etcdpath - location in etcd to store configs - default: '/config/cidrs'

#### Example

etcdpath="/ojo/cidrs" listenaddr='127.0.0.1' debug='true' etcdaddr='localhost' ./gw-etcd.py
