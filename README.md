# cidrmgr
a restful API for tracking CIDRs, backed in etcd

# Examples

```
ip-10-1-1-159:~ dland$ http http://127.0.0.1:8080/cidr
HTTP/1.0 200 OK
Content-Length: 170
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:13:38 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.16.0.0/16",
    "172.17.0.0/16",
    "172.18.1.0/24",
    "172.18.2.0/24",
    "172.18.3.0/24",
    "172.18.4.0/24",
    "172.18.5.0/24",
    "172.18.6.0/24",
    "172.19.0.0/16",
    "172.20.0.0/16"
]

ip-10-1-1-159:~ dland$ http DELETE http://127.0.0.1:8080/cidr/172.18.1.0/24
HTTP/1.0 200 OK
Content-Length: 16
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:13:47 GMT
Server: WSGIServer/0.1 Python/2.7.10

{
    "status": "ok"
}

ip-10-1-1-159:~ dland$ http http://127.0.0.1:8080/cidr
HTTP/1.0 200 OK
Content-Length: 153
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:13:49 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.16.0.0/16",
    "172.17.0.0/16",
    "172.18.2.0/24",
    "172.18.3.0/24",
    "172.18.4.0/24",
    "172.18.5.0/24",
    "172.18.6.0/24",
    "172.19.0.0/16",
    "172.20.0.0/16"
]

ip-10-1-1-159:~ dland$ http POST http://127.0.0.1:8080/cidr
HTTP/1.0 200 OK
Content-Length: 17
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:14:46 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.21.0.0/16"
]

ip-10-1-1-159:~ dland$ http http://127.0.0.1:8080/cidr
HTTP/1.0 200 OK
Content-Length: 170
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:14:50 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.16.0.0/16",
    "172.17.0.0/16",
    "172.18.2.0/24",
    "172.18.3.0/24",
    "172.18.4.0/24",
    "172.18.5.0/24",
    "172.18.6.0/24",
    "172.19.0.0/16",
    "172.20.0.0/16",
    "172.21.0.0/16"
]

ip-10-1-1-159:~ dland$ http POST http://127.0.0.1:8080/cidr customcidr=172.18.4.0/24
HTTP/1.0 500 Internal Server Error
Content-Length: 749
Content-Type: text/html; charset=UTF-8
Date: Thu, 23 Feb 2017 04:15:15 GMT
Server: WSGIServer/0.1 Python/2.7.10

    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html>
        <head>
            <title>Error: 500 Internal Server Error</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd;
                    padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error: 500 Internal Server Error</h1>
            <p>Sorry, the requested URL <tt>&#039;http://127.0.0.1:8080/cidr&#039;</tt>
               caused an error:</p>
            <pre>Error: cidr not available</pre>
        </body>
    </html>

ip-10-1-1-159:~ dland$ http POST http://127.0.0.1:8080/cidr customcidr=172.18.7.0/24
HTTP/1.0 200 OK
Content-Length: 17
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:15:26 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.18.7.0/24"
]

ip-10-1-1-159:~ dland$ http POST http://127.0.0.1:8080/cidr bitrange=24
HTTP/1.0 200 OK
Content-Length: 17
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:15:40 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.18.0.0/24"
]

ip-10-1-1-159:~ dland$ http POST http://127.0.0.1:8080/cidr bitrange=24 numberranges=2
HTTP/1.0 200 OK
Content-Length: 34
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:16:01 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.18.1.0/24",
    "172.18.8.0/24"
]

ip-10-1-1-159:~ dland$ http http://127.0.0.1:8080/cidr
HTTP/1.0 200 OK
Content-Length: 238
Content-Type: application/json
Date: Thu, 23 Feb 2017 04:16:05 GMT
Server: WSGIServer/0.1 Python/2.7.10

[
    "172.16.0.0/16",
    "172.17.0.0/16",
    "172.18.0.0/24",
    "172.18.1.0/24",
    "172.18.2.0/24",
    "172.18.3.0/24",
    "172.18.4.0/24",
    "172.18.5.0/24",
    "172.18.6.0/24",
    "172.18.7.0/24",
    "172.18.8.0/24",
    "172.19.0.0/16",
    "172.20.0.0/16",
    "172.21.0.0/16"
]
```
