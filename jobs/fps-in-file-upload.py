import sys
import getopt
import os
import shutil
import logging
import pysftp
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
import zooconfig
import hdfFileService


def main(args):
    print '### fps-in-file-upload service - started'
    # Get zookeeper url from arguments
    zookeeper_url = ''
    hdfs_path = ''
    ftp_path = ''
    archive_folder = ''
    try:
        opts, args = getopt.getopt(args, "zhfa:", ['zookeeper=', 'hdfsPath=', 'ftpPath=', 'archivePath='])
    except getopt.GetoptError:
        print 'fps-in-file-upload.py -z (--zookeeper) <zookeeper_url>'
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
        print 'Zookeeper url not provided'
        sys.exit(2)
    if hdfs_path == '':
        print 'Hdfs path not provided'
        sys.exit(2)
    if ftp_path == '':
        print 'FTP path not provided'
        sys.exit(2)
    if archive_folder == '':
        print 'Hdfs archive path not provided'
        sys.exit(2)

    zookeeper_config = '/fps/incoming/fps-in-file-upload/'

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)

    # HDFS connection
    file_service = check_active_name_node(config)
    local_path = os.path.dirname(os.path.realpath(__file__))
    print '[HDFS Download file] Download to path : {0}'.format(local_path)
    download_path = file_service.download(hdfs_path, local_path)
    print '[HDFS Download file] Files have been download to path : {0}'.format(download_path)
    
   

    # sftp connection
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(config["ftp_host"], username=config["ftp_username"], password=config["ftp_password"], port=int(config["ftp_port"]), cnopts=cnopts) as sftp:
        print('### Connected to SFTP')
        sftp.put_d(download_path, ftp_path)
        print('### Files have been copied to SFTP')
    
    # archive files in hdfs
    files = file_service.get_files(hdfs_path)
    
    for f in files:
        file_path = '%s/%s' % (hdfs_path, f[0])
        print '[HDFS Achive file] File {0} have been archived to path : {1}'.format(file_path, archive_folder)
        file_service.archive_file(f[0], file_path, archive_folder)

    shutil.rmtree(download_path)
    print '### fps-in-file-upload service - finished'


def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']
    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    try:
        print('### Test active name node : ' + active_name_node)
        file_service.get_files(config["hdfs_files_path"])
    except Exception as exc:
        print('### Name node : ' + active_name_node + ' is not active!')
        active_name_node = config['hdfs_name_node_2']

    try:
        print('### Test active name node : ' + active_name_node)
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
