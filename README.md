## hermod-fps
Hermod FPS include scripts:
- Faster Payment Cron FTP Jobs
- Faster Payment Oozie Job Processor
- Faster Payment Oozie Job Ackonwledgement Uploader
- Faster Payment Oozie Job Confirmation Uploader
- Faster Payment Oozie Job File Monitor

## Configuration:
All configuration should be added to zookeeper. All configs are in _config/<env>/zoo.<env>.txt file

## Upload to environment:
The scripts should be uploaded to: 
- fps-in-file-download.py - connector-0 node

## Run
To run scripts execute the powershell script in run/<env>/run-fps-scripts.sid.ps1
