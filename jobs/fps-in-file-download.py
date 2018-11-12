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

def main(args):
    print '### fps-in-file-download service - started'
    # Get zookeeper url from arguments
    zookeeper_url = ''
    try:
        opts, args = getopt.getopt(args, "z:", ['zookeeper='])
    except getopt.GetoptError:
        print 'fps-in-file-download.py -z (--zookeeper) <zookeeper_url>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-z' or opt == '--zookeeper':
            zookeeper_url = arg

    if zookeeper_url == '':
        print 'Zookeeper url not provided'
        sys.exit(2)
    
    zookeeper_config = '/fps/outgoing/fps-in-file-download/'

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    
    # create dir locally if it does not exist
    print config
    local_dir = os.getcwd() + '/' + config['ftp_dir']
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # HDFS connection
    file_service = check_active_name_node(config)

    # sftp connection
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(config["ftp_host"], username=config["ftp_username"], password=config["ftp_password"], port=int(config["ftp_port"]), cnopts=cnopts) as sftp:
        print('### Connected to SFTP')
        print('### Moving to ' + config["ftp_dir"])
        
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
                    print('### Downloading: ' + f.filename)
                    localpath = local_dir + '/' + f.filename
                    sftp.get(f.filename, localpath=localpath, preserve_mtime=True)
                    
                    # Checking if file exists on HDFS
                    hdfs_path = config["hdfs_files_path"] + '/' + f.filename
                    print('### Checking if file exists on HDFS : ' + hdfs_path)
                     
                    if file_service.get_file_status(hdfs_path) != None:
                        # If file exists in HDFS move file to error dir with unique name
                        print('### File exists in HDFS directory, moving to error folder')
                        unique_filename = ticksString + '.' + f.filename + '.error'
                        error_path = config["ftp_error_dir"] + '/' + unique_filename
                        print('### MOVE from : ' + config["ftp_dir"]+'/'+f.filename+ ' TO : ' + error_path)
                        sftp.rename(f.filename, error_path)
                    
                    else:
                        # If file does not exist in HDFS upload file
                        print('### Uploading local file: ' + localpath + ' to ' + hdfs_path + ' on HDFS')
                        file_service.upload_file(localpath, config["hdfs_files_path"])
                                                
                        # When file has been uploaded to HDFS move file to archive dir with unique name on ftp
                        unique_filename = ticksString + '.' + f.filename + '.archive'
                        archive_path = config["ftp_archive_dir"] + '/' + unique_filename
                        print('### MOVE from : ' + config["ftp_dir"]+'/'+f.filename+ ' TO : ' + archive_path)
                        sftp.rename(f.filename, archive_path)

                except Exception as exc:
                    print '### Error during processing file: %s' % (f.filename), exc
                    
                    # On exception move file to error dir with unique name
                    unique_filename = ticksString + '.' + f.filename + '.error'
                    error_path = config["ftp_error_dir"] + '/' + unique_filename
                    print('### MOVE from : ' + config["ftp_dir"]+'/'+f.filename + ' TO : ' + error_path)
                    sftp.rename(f.filename, error_path)

        print('### Removing local temporary directory')
        shutil.rmtree(local_dir)
        print '### fps-in-file-download service - finished'

def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        print('### Test active name node : ' + active_name_node)
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path"])
    except Exception as exc:
        print('### Name node : ' + active_name_node + ' is not active!')
        active_name_node = config['hdfs_name_node_2']

    try:
        print('### Test active name node : ' + active_name_node)
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path"])
    except Exception as exc:
        print('### Name node : ' + active_name_node + ' is not active!')
        active_name_node = config['hdfs_name_node_1']

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    print('### Active name node : ' + active_name_node)
    return file_service

print str(sys.argv)
logging.basicConfig()
main(sys.argv[1:])
