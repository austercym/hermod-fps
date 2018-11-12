echo "#### DEPLOYMENT START #### "
echo "#### REMOVING OLD FILES ####"
hadoop fs -rm -R /lagertha/hermod/fps/jobs/jobs
echo "#### COPY NEW FILES ####"
hadoop fs -put -f ./jobs /lagertha/hermod/fps/jobs
echo "#### DEPLOYMENT END ####" 
