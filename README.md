# cidrmgr
a restful API for tracking CIDRs, backed in etcd

# seeding intial entry

This setup will fail unless there is at least one entry, which can be created like:

etcdctl set <your_etcdpath_here>/172.31.0.0_16 "default vpc cidr"

# Running

## etcd version
etcdpath="/ojo/cidrs" listenaddr='127.0.0.1' debug='true' etcdaddr='localhost' ./pygw.py

## etcd only

etcdaddr - etcd server - default: 'localhost'

etcdport - etcd port - default: '2379'

etcdpath - location in etcd to store configs - default: '/config/cidrs'

## all

debug - debug mode - default: 'false'

listenaddr - IP to listen on  - default: '0.0.0.0'

listenport - port to listen on - default: '8090'

