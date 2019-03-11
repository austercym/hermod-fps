import sys
import getopt
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'fps-ack-file-generator'))
import zooconfig
import hdfFileService
import hbaseService
import xmlConverter
import arrow
import kafkaLogger
from datetime import datetime, timedelta, time

def main(args):
    log_to_console('fps-ack-file-generator - started')
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

    zookeeper_config = '/fps/outgoing/fps-ack-file-generator/'

    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    file_service = check_active_name_node(config)
    hbase_service = hbaseService.HbaseService(config)
    kafka_logger = kafkaLogger.KafkaLogger(config)

    # 1. Get transaction from hbase
    fps_files = hbase_service.get_ack_messages()
    for fps_file in fps_files:
        try:
            # 2. Convert to XML
            ack_file_content = convert_to_xml(fps_file)
            #print '[XML] Converted xml : {0}'.format(ack_file_content)
            ack_file_name = 'FPS_{0}.xml'.format(fps_file.transaction.transaction_id)
            # 3. Write XML to file
            with open(ack_file_name, "w+") as f:
                f.write(ack_file_content)
            
            # 4. Upload file to HDFS
            if(fps_file.transaction.status == 'ACK'):
                log_to_console('[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_ack"]))
                file_service.upload_file(ack_file_name, config["hdfs_files_path_ack"])
                # 5. Update status in Hbase
                log_to_console('[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key))
                hbase_service.update_outgoing_ack(fps_file.transaction.row_key, "ACK_UPLOADED", ack_file_name)
                # 7. Log to kafka
                kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_ACK_UPLOADED')
            elif(fps_file.transaction.status == 'NACK'):

                log_to_console('[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_nack"]))
                log_to_console('[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key))
                file_service.upload_file(ack_file_name, config["hdfs_files_path_nack"])
                # 5. Update status in Hbase
                hbase_service.update_outgoing_ack(fps_file.transaction.row_key, "NACK_UPLOADED", ack_file_name)
                # 7. Log to kafka
                kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_NACK_UPLOADED')
            elif(fps_file.transaction.status == 'CONFIRMED'):
                log_to_console('[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_ack"]))
                file_service.upload_file(ack_file_name, config["hdfs_files_path_ack"])
                # 5. Update status in Hbase
                log_to_console('[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key))
                hbase_service.update_outgoing_ack_file_name(fps_file.transaction.row_key, ack_file_name)
                # 7. Log to kafka
                kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_ACK_UPLOADED')
            os.remove(ack_file_name)
        except Exception as exc:
            log_to_console('Error during creating ack file: {0}'.format(str(exc)))

    log_to_console('fps-ack-file-generator - finished')

#region HDFS


def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        log_to_console('Test active name node : {0}'.format(active_name_node))
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path_ack"])
    except Exception as exc:
        log_to_console('Name node : {0} is not active!'.format(active_name_node))
        active_name_node = config['hdfs_name_node_2']

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    log_to_console('Active name node : {0}'.format(active_name_node))
    return file_service

#endregion

#region convert to xml

def convert_to_xml(fps_file):
    log_to_console('[XML] Convert model to XML')
    date = arrow.utcnow()
    processing_date_bst = date.format('ddd MMM DD HH:mm:ss') + ' BST ' + date.format('YYYY')
    processing_date_short = date.format('YYYY-MM-DD')
    status = 'complete'
    if(fps_file.transaction.status == 'ACK'):
        status = 'complete'
    elif(fps_file.transaction.status == 'NACK'):
        status = 'failure'
    xml_converter = xmlConverter.XMLConverter()
    return xml_converter.convert(fps_file, processing_date_bst, processing_date_short, status)

#endregion

#region logging

def log_to_console(message):
    processing_date = datetime.utcnow()
    processing_date_string = str(processing_date)
    print '{0} - {1}'.format(processing_date_string, message)

#endregion
main(sys.argv[1:])
