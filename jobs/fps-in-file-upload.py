import sys
import getopt
import os
import shutil
import logging
import pysftp
from os import listdir
from os.path import isfile, join
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
import zooconfig
import hdfFileService
from datetime import datetime, timedelta, time

def main(args):
    log_to_console('fps-in-file-upload service - started')
    # Get zookeeper url from arguments
    zookeeper_url = ''
    hdfs_path = ''
    ftp_path = ''
    archive_folder = ''
    try:
        opts, args = getopt.getopt(args, "zhfa:", ['zookeeper=', 'hdfsPath=', 'ftpPath=', 'archivePath='])
    except getopt.GetoptError:
        log_to_console('fps-in-file-upload.py -z (--zookeeper) <zookeeper_url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-z' or opt == '--zookeeper':
            zookeeper_url = arg
        if opt == '-h' or opt == '--hdfsPath':
            hdfs_path = arg
        if opt == '-f' or opt == '--ftpPath':
            ftp_path = arg
        if opt == '-a' or opt == '--archivePath':
            archive_folder = arg
    if zookeeper_url == '':
        log_to_console('Zookeeper url not provided')
        sys.exit(2)
    if hdfs_path == '':
        log_to_console('Hdfs path not provided')
        sys.exit(2)
    if ftp_path == '':
        log_to_console('FTP path not provided')
        sys.exit(2)
    if archive_folder == '':
        log_to_console('Hdfs archive path not provided')
        sys.exit(2)

    zookeeper_config = '/fps/outgoing/fps-in-file-upload/'

    config = zooconfig.get_config(zookeeper_url, zookeeper_config)

    # HDFS connection
    file_service = check_active_name_node(config)
    local_path = os.path.dirname(os.path.realpath(__file__))
    files = file_service.get_files(hdfs_path)
    if(len(files) > 0):
        log_to_console('[HDFS Download file] Download to path : {0}'.format(local_path))
        download_path = file_service.download(hdfs_path, local_path)
        log_to_console('[HDFS Download file] Files have been download to path : {0}'.format(download_path))
        onlyfiles = [f for f in listdir(download_path) if isfile(join(download_path, f))]
        for f in onlyfiles:
            log_to_console('[SFTP file to upload] File {0} will be uploaded'.format(f))
        # sftp connection
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        #try:
        with pysftp.Connection(config["ftp_host"], username=config["ftp_username"], password=config["ftp_password"], port=int(config["ftp_port"]), cnopts=cnopts) as sftp:
            log_to_console('[SFTP upload files] Connected to SFTP')
            sftp.put_d(download_path, ftp_path)
            log_to_console('[SFTP upload files] Files have been uploaded to SFTP')
        #except Exception as exc:
        #    log_to_console('[SFTP upload files] ERROR while uploading the files : {0}'.format(str(exc)))
        # archive files in hdfs
        #files = file_service.get_files(hdfs_path)
        
        for f in files:
            date = datetime.utcnow()
            date_string = str(date)
            epoch = datetime.utcfromtimestamp(0)
            ticks = int((date - epoch).total_seconds() * 1000)
            date_ticks_string = str(ticks)
            
            file_path = '%s/%s' % (hdfs_path, f[0])
            log_to_console('[HDFS Achive file] File {0} have been archived to path : {1}'.format(file_path, archive_folder))
            file_service.archive_file(date_ticks_string + '.' + f[0], file_path, archive_folder)

        shutil.rmtree(download_path)
        log_to_console('fps-in-file-upload service - finished')


def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        log_to_console('Test active name node : ' + active_name_node)
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path"])
    except Exception as exc:
        log_to_console('Name node : ' + active_name_node + ' is not active!')
        active_name_node = config['hdfs_name_node_2']

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    log_to_console('Active name node : ' + active_name_node)
    return file_service


def log_to_console(message):
    processing_date = datetime.utcnow()
    processing_date_string = str(processing_date)
    print '{0} - {1}'.format(processing_date_string, message)

print str(sys.argv)
logging.basicConfig()
main(sys.argv[1:])
