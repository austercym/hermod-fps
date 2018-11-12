echo "#### RUN FPS IN FILE UPLOAD START"
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python fps-in-file-upload.py --zookeeper hdf-g1-0.node.consul:2181 --hdfsPath /lagertha/hermod/data/fps/ack --ftpPath /fps/ack --archivePath /lagertha/hermod/data/fps/ack-archive
echo "#### IN FILE UPLOAD END"
