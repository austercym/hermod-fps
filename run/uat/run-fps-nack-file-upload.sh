echo "#### RUN FPS IN FILE UPLOAD START"
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python /home/svc_v3fps/hermod-fps/jobs/fps-in-file-upload.py --zookeeper ambari-slave-0.node.consul:2181 --hdfsPath /lagertha/hermod/data/fps/nack --ftpPath /v3/fps/ack --archivePath /lagertha/hermod/data/fps/nack-archive
echo "#### IN FILE UPLOAD END"
