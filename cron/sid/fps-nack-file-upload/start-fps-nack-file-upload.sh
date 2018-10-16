#!/bin/bash
*/15 * * * * /home/svc_v3fps/hermod-fps/hermod-fps/hermod-fps/jobs/run-fps-nack-file-upload.sh &> run-fps-nack-file-upload.log &
echo $! > run-fps-nack-file-upload.pid
