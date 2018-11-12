echo "#### RUN BACS IN FILE MONITORING"
. /home/svc_v3fps/hermod-fps/fps-monitoring-env/bin/activate
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
python /home/svc_v3fps/hermod-fps/jobs/fps-file-monitoring.py --zookeeper ambari-slave-0.node.consul:2181
echo "#### IN FILE MONITORING END"
