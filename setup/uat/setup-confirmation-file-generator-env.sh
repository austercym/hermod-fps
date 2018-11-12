#!/bin/bash
pip install virtualenv
virtualenv ../../fps-confirmation-env
cd ../../fps-confirmation-env
. ./bin/activate
pip install pyxb kazoo thrift python-dateutil gssapi hdfs[kerberos] xmltodict kafka kafka-python avro PyKerberos py4j arrow

pip install gssapi
pip install hdfs[kerberos]
