echo "#### RUN FPS INCOMING GENERATOR"
. /home/svc_v3fps/hermod-fps/hermod-fps/fps-incoming-env/bin/activate
kinit -kt /etc/security/keytabs/svc_v3fps.keytab svc_v3fps
/usr/hdp/current/spark-client/bin/spark-submit --master local --jars /usr/hdp/current/phoenix-client/phoenix-client.jar,/usr/hdp/current/phoenix-client/lib/phoenix-spark-4.7.0.2.6.4.0-91.jar --conf "spark.executor.extraClassPath=/usr/hdp/current/phoenix-client/phoenix-client.jar" ./jobs/fps-incoming-file-generator.py --zookeeper $1
echo "#### FPS INCOMING GENERATOR END"