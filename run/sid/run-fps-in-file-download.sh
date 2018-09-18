echo "#### RUN FPS IN FILE DOWNLOAD START"
cd /home/svc_fps/hermod-fps/hermod-fps/jobs/
sudo su -c 'kinit -kt /etc/security/keytabs/svc_fps.keytab svc_fps;python fps-in-file-download.py --zookeeper sid-hdp-g1-0.node.sid.consul:2181' svc_fps
echo "#### IN FILE DOWNLOAD END"
