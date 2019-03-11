echo "#### RUN BACS IN FILE PROCESS"
. /home/svc_v3fps/hermod-fps/fps-process-env/bin/activate
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
/usr/hdp/current/spark2-client/bin/spark-submit --master local --jars /usr/hdp/current/phoenix-client/phoenix-client.jar,/usr/hdp/current/phoenix-client/lib/phoenix-spark-5.0.0.3.1.0.0-78.jar --conf "spark.executor.extraClassPath=/usr/hdp/current/phoenix-client/phoenix-client.jar" fps-in-file-process.py --zookeeper sid-hdp-g1-0.node.sid.consul:2181
echo "#### IN FILE BACS PROCESS END"
