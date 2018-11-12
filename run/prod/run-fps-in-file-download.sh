echo "#### RUN FPS IN FILE download START"
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python /home/svc_v3fps/hermod-fps/jobs/fps-in-file-download.py --zookeeper hdf-g1-0.node.consul:2181
echo "#### IN FILE download END"
