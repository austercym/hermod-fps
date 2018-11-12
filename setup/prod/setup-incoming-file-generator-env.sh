#!/bin/bash
pip install virtualenv
virtualenv ../../fps-incoming-env
cd ../../fps-incoming-env
. ./bin/activate
pip install pyxb kazoo thrift python-dateutil gssapi hdfs[kerberos] xmltodict kafka kafka-python avro PyKerberos py4j arrow
