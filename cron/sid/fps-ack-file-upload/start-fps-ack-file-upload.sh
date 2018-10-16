#!/bin/bash
*/15 * * * * /home/svc_v3fps/hermod-fps/hermod-fps/hermod-fps/jobs/run-fps-ack-file-upload.sh >> /home/svc_v3fps/hermod-fps/hermod-fps/hermod-fps/jobs/run-fps-ack-file-upload.log 2>&1
echo $! > run-fps-ack-file-upload.pid
