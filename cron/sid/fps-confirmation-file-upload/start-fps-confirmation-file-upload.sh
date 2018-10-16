#!/bin/bash
*/15 * * * * /home/svc_v3fps/hermod-fps/hermod-fps/hermod-fps/jobs/run-fps-confirmation-file-upload.sh &> run-fps-confirmation-file-upload.log &
echo $! > run-fps-confirmation-file-upload.pid
