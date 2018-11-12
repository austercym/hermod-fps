echo "#### RUN FPS IN FILE UPLOAD START"
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python fps-in-file-upload.py --zookeeper ambari-slave-0.node.consul:2181 --hdfsPath /lagertha/hermod/data/fps/nack --ftpPath /fps/nack --archivePath /lagertha/hermod/data/fps/nack-archive
echo "#### IN FILE UPLOAD END"
