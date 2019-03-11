echo "#### RUN FPS IN FILE UPLOAD START"
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python /home/svc_v3fps/hermod-fps/jobs/fps-in-file-upload.py --zookeeper sid-hdp-g1-0.node.sid.consul:2181 --hdfsPath /lagertha/hermod/data/fps/incoming --ftpPath /v3/fps/incoming --archivePath /lagertha/hermod/data/fps/incoming-archive
echo "#### IN FILE UPLOAD END"
