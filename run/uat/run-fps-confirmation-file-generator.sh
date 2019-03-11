echo "#### RUN FPS CONFIRMATION GENERATOR"
. /home/svc_v3fps/hermod-fps/fps-confirmation-env/bin/activate
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
/usr/hdp/current/spark2-client/bin/spark-submit --master local --jars /usr/hdp/current/phoenix-client/phoenix-client.jar,/usr/hdp/current/phoenix-client/lib/phoenix-spark-5.0.0.3.1.0.0-78.jar --conf "spark.executor.extraClassPath=/usr/hdp/current/phoenix-client/phoenix-client.jar" fps-confirmation-file-generator.py --zookeeper ambari-slave-0.node.consul:2181
echo "#### FPS CONFIRMATION GENERATOR END"
