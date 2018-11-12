#!/bin/bash
echo "### START OOZIE JOB FOR ENV : "
oozie job -oozie http://hdp-g1-2.node.consul:11000/oozie -config /home/svc_v3fps/hermod-fps/_config/prod/fps-confirmation-file-generator.properties -run
echo "### OOZIE JOB CREATED"
