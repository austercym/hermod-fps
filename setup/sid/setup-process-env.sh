#!/bin/bash
pip install virtualenv
virtualenv ../../fps-process-env
cd ../../fps-process-env
. ./bin/activate
pip install pyxb kazoo thrift python-dateutil gssapi hdfs[kerberos] xmltodict kafka kafka-python avro PyKerberos py4j requests
