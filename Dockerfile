FROM alpine
MAINTAINER Doug Land <dland@ojolabs.com>

COPY python-etcd /app/python-etcd
RUN \
    apk update \
    && apk add python py-pip ca-certificates \
    && pip install netaddr bottle tornado boto3 \
    && cd /app/python-etcd/ \
    && python setup.py install \
    && cd / \
    && rm -rf /app/python-etcd \
    && rm -rf /var/cache/apk/*
COPY gw-aws.py /app/gw.py
expose 8090
CMD python /app/gw.py
