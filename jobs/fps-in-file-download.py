import sys
import getopt
import os
import shutil
import logging
import pysftp
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
import zooconfig
import hdfFileService
from datetime import datetime, timedelta, time

def main(args):
    log_to_console('fps-in-file-download service - started')
    # Get zookeeper url from arguments
    zookeeper_url = ''
    try:
        opts, args = getopt.getopt(args, "z:", ['zookeeper='])
    except getopt.GetoptError:
        log_to_console('fps-in-file-download.py -z (--zookeeper) <zookeeper_url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-z' or opt == '--zookeeper':
            zookeeper_url = arg

    if zookeeper_url == '':
        log_to_console('Zookeeper url not provided')
        sys.exit(2)
    
    zookeeper_config = '/fps/outgoing/fps-in-file-download/'

    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    
    # create dir locally if it does not exist
    local_dir = os.getcwd() + '/' + config['ftp_dir']
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # HDFS connection
    file_service = check_active_name_node(config)

    # sftp connection
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(config["ftp_host"], username=config["ftp_username"], password=config["ftp_password"], port=int(config["ftp_port"]), cnopts=cnopts) as sftp:
      
        with sftp.cd(config["ftp_dir"]):
            # Get files from ftp
            files = sftp.listdir_attr()
            # Download files
            for f in files:
                try:
                    # Setup processing date
                    processingDate = datetime.utcnow()
                    epoch = datetime.utcfromtimestamp(0)
                    ticks = int((processingDate - epoch).total_seconds() * 1000)
                    ticksString = str(ticks)
                    
                    # Download file
                    log_to_console('### Downloading: '.format(f.filename))
                    localpath = local_dir + '/' + f.filename
                    sftp.get(f.filename, localpath=localpath, preserve_mtime=True)
                    
                    # Checking if file exists on HDFS
                    hdfs_path = config["hdfs_files_path"] + '/' + f.filename
                    log_to_console('### Checking if file exists on HDFS : {0}'.format(hdfs_path))
                     
                    if file_service.get_file_status(hdfs_path) != None:
                        # If file exists in HDFS move file to error dir with unique name
                        log_to_console('File exists in HDFS directory, moving to error folder')
                        unique_filename = ticksString + '.' + f.filename + '.error'
                        error_path = config["ftp_error_dir"] + '/' + unique_filename
                        log_to_console('MOVE from : {0}/{1} TO : {2} '.format(config["ftp_dir"], f.filename, error_path))
                        sftp.rename(f.filename, error_path)
                    
                    else:
                        # If file does not exist in HDFS upload file
                        log_to_console('Uploading local file: {0} to {1} on HDFS'.format(localpath, hdfs_path))
                        file_service.upload_file(localpath, config["hdfs_files_path"])
                                                
                        # When file has been uploaded to HDFS move file to archive dir with unique name on ftp
                        unique_filename = ticksString + '.' + f.filename + '.archive'
                        archive_path = config["ftp_archive_dir"] + '/' + unique_filename
                        log_to_console('MOVE from : {0}/{1} TO : {2}'.format(config["ftp_dir"], f.filename, archive_path))
                        sftp.rename(f.filename, archive_path)

                except Exception as exc:
                    log_to_console('Error during processing file: {0} - error : {1}'.format(f.filename, str(exc)))
                    # On exception move file to error dir with unique name
                    unique_filename = ticksString + '.' + f.filename + '.error'
                    error_path = config["ftp_error_dir"] + '/' + unique_filename
                    log_to_console('MOVE from : {0}/{1} TO : {2} '.format(config["ftp_dir"], f.filename, error_path))
                    sftp.rename(f.filename, error_path)

        log_to_console('Removing local temporary directory')
        shutil.rmtree(local_dir)
        log_to_console('fps-in-file-download service - finished')

def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        log_to_console('Test active name node : {0}'.format(active_name_node))
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path"])
    except Exception as exc:
        log_to_console('Name node : {0} is not active!'.format(active_name_node))
        active_name_node = config['hdfs_name_node_2']

    try:
        log_to_console('Test active name node : {0}'.format(active_name_node))
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path"])
    except Exception as exc:
        log_to_console('Name node : {0} is not active!'.format(active_name_node))
        active_name_node = config['hdfs_name_node_1']

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    log_to_console('Active name node : {0}'.format(active_name_node))
    return file_service

#region logging


def log_to_console(message):
    processing_date = datetime.utcnow()
    processing_date_string = str(processing_date)
    print '{0} - {1}'.format(processing_date_string, message)

#endregion

main(sys.argv[1:])
