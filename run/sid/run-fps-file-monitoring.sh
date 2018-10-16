echo "#### RUN BACS IN FILE MONITORING"
. /home/svc_v3fps/hermod-fps/hermod-fps/fps-monitoring-env/bin/activate
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python /home/svc_v3fps/hermod-fps/hermod-fps/jobs/fps-file-monitoring.py --zookeeper sid-hdp-g1-0.node.sid.consul:2181
echo "#### IN FILE MONITORING END"
