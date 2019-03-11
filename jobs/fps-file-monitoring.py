import sys
import getopt
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
import zooconfig
import hdfFileService
import kafkaLogger
from datetime import datetime, timedelta, time

def main(args):
    log_to_console('fps-file-monitoring - started')
    zookeeper_url = ''
    try:
        opts, args = getopt.getopt(
            args, "z:", ['zookeeper='])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-z' or opt == '--zookeeper':
            zookeeper_url = arg

    if zookeeper_url == '':
        sys.exit(2)

    zookeeper_config = '/fps/monitoring/fps-file-monitoring/'

    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    file_service = check_active_name_node(config)
    kafka_logger = kafkaLogger.KafkaLogger(config)

    # 1. Get incoming files 
    files = file_service.get_files(config["hdfs_files_path_incoming"])
    kafka_logger.file_hdfs_stats(len(files), 'incoming')
    
    # 2. Get incoming achived files
    files = file_service.get_files(config["hdfs_files_path_incoming_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'incoming-archive')
    
    # 3. Get incoming error files
    files = file_service.get_files(config["hdfs_files_path_incoming_error"])
    kafka_logger.file_hdfs_stats(len(files), 'incoming-error')
    
    # 4. Get outgoing files
    files = file_service.get_files(config["hdfs_files_path_outgoing"])
    kafka_logger.file_hdfs_stats(len(files), 'outgoing')

    # 5. Get outgoing achived files
    files = file_service.get_files(config["hdfs_files_path_outgoing_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'outgoing-archive')

    # 6. Get outgoing error files
    files = file_service.get_files(config["hdfs_files_path_outgoing_error"])
    kafka_logger.file_hdfs_stats(len(files), 'outgoing-error')
    
    # 7. Get ack files
    files = file_service.get_files(config["hdfs_files_path_ack"])
    kafka_logger.file_hdfs_stats(len(files), 'ack')

    # 8. Get ack achived files
    files = file_service.get_files(config["hdfs_files_path_ack_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'ack-archive')
    
    # 9. Get nack files
    files = file_service.get_files(config["hdfs_files_path_nack"])
    kafka_logger.file_hdfs_stats(len(files), 'nack')

    # 10. Get nack achived files
    files = file_service.get_files(config["hdfs_files_path_nack_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'nack-archive')

    # 9. Get nack files
    files = file_service.get_files(config["hdfs_files_path_nack"])
    kafka_logger.file_hdfs_stats(len(files), 'nack')

    # 10. Get nack achived files
    files = file_service.get_files(config["hdfs_files_path_nack_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'nack-archive')

    # 9. Get nack files
    files = file_service.get_files(config["hdfs_files_path_nack"])
    kafka_logger.file_hdfs_stats(len(files), 'nack')

    # 10. Get nack achived files
    files = file_service.get_files(config["hdfs_files_path_nack_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'nack-archive')

    # 9. Get nack files
    files = file_service.get_files(config["hdfs_files_path_nack"])
    kafka_logger.file_hdfs_stats(len(files), 'nack')

    # 10. Get nack achived files
    files = file_service.get_files(config["hdfs_files_path_nack_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'nack-archive')

    # 11. Get confirmation files
    files = file_service.get_files(config["hdfs_files_path_confirmation"])
    kafka_logger.file_hdfs_stats(len(files), 'confirmation')
    
    # 12. Get confirmation achived files
    files = file_service.get_files(config["hdfs_files_path_confirmation_archive"])
    kafka_logger.file_hdfs_stats(len(files), 'confirmation-archive')

    log_to_console('fps-file-monitoring - finished')

#region HDFS


def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        log_to_console('Test active name node : {0}'.format(active_name_node))
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path_outgoing"])
    except Exception as exc:
        log_to_console('Name node : {0} is not active!'.format(active_name_node))
        active_name_node = config['hdfs_name_node_2']

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    log_to_console('Active name node : {0}'.format(active_name_node))
    return file_service

#endregion

#region logging


def log_to_console(message):
    processing_date = datetime.utcnow()
    processing_date_string = str(processing_date)
    print '{0} - {1}'.format(processing_date_string, message)

#endregion

main(sys.argv[1:])
