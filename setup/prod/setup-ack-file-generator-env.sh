#!/bin/bash
pip install virtualenv
virtualenv ../../fps-ack-env
cd ../../fps-ack-env
. ./bin/activate
pip install pyxb kazoo thrift python-dateutil gssapi hdfs[kerberos] xmltodict kafka kafka-python avro PyKerberos py4j arrow
