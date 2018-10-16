#!/bin/bash
20 * * * * /home/svc_v3fps/hermod-fps/hermod-fps/hermod-fps/jobs/run-fps-incoming-file-upload.sh &> run-fps-incoming-file-upload.log &
echo $! > run-fps-incoming-file-upload.pid
