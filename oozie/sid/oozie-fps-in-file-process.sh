#!/bin/bash
echo "### START OOZIE JOB FOR ENV : "
echo $1
oozie job -oozie http://sid-hdp-g1-2.node.sid.consul:11000/oozie -config /home/svc_v3fps/hermod-fps/_config/sid/fps-in-file-process.properties -run
echo "### OOZIE JOB CREATED"
