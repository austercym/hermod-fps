echo "#### RUN FPS IN FILE UPLOAD START"
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python fps-in-file-upload.py --zookeeper hdf-g1-0.node.consul:2181 --hdfsPath /lagertha/hermod/data/fps/incoming --ftpPath /fps/incoming --archivePath /lagertha/hermod/data/fps/incoming-archive
echo "#### IN FILE UPLOAD END"
