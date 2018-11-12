#!/bin/bash
echo "### START OOZIE JOB FOR ENV : "
oozie job -oozie http://ambari-slave-0.node.consul:11000/oozie -config /home/svc_v3fps/hermod-fps/_config/uat/fps-ack-file-cat .properties -run
echo "### OOZIE JOB CREATED"
