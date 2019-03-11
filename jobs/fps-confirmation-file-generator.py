import sys
import getopt
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'fps-confirmation-file-generator'))
import zooconfig
import hdfFileService
import hbaseService
import xmlConverter
import arrow
import random
import zipfile
import kafkaLogger
from datetime import datetime, timedelta, time

def main(args):
    log_to_console('fps-confirmation-file-generator - started')
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

    zookeeper_config = '/fps/outgoing/fps-confirmation-file-generator/'
    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    file_service = check_active_name_node(config)
    hbase_service = hbaseService.HbaseService(config)
    kafka_logger = kafkaLogger.KafkaLogger(config)
    # 1. Get transaction from hbase
    fps_files = hbase_service.get_confirmation_messages()
    ack_files = file_service.get_files(config["hdfs_files_ack_archive_path"])
    log_to_console('[HDFS files in ack archive dir] {}'.format(str(len(ack_files))))
    fps_files_acknowledged = []
    fps_files_confirmed = []
    fps_files_ids = ""

    for fps_file in fps_files:
        log_to_console('[Hbase get acknowledged file]  {0}'.format(fps_file.transaction.transaction_id))
        for ack_file in ack_files:
            log_to_console('[HDFS get files ack_archive ]  {0}'.format(ack_file[0]))
            if fps_file.transaction.transaction_id in ack_file[0]:
                fps_files_acknowledged.append(fps_file)
                fps_files_ids = fps_files_ids+"'"+fps_file.transaction.transaction_id + "',"
                break
    confirmed_message = []
    if(fps_files_ids):
        log_to_console('[Hbase get confirmed for ]  {0}'.format(fps_files_ids))
        confirmed_message = hbase_service.get_confirmed(fps_files_ids[:-1])
    
    for fps_file in fps_files_acknowledged:
        for confirmed_file in confirmed_message:
            if fps_file.transaction.transaction_id == confirmed_file.row_key:
                fps_file.transaction.status = confirmed_file.status
                fps_file.transaction.rejection_reason = confirmed_file.rejection_reason
                fps_files_confirmed.append(fps_file)
                break

    for fps_file in fps_files_confirmed:
        try:
            # 2. Convert to XML
            kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_CONFIRMED')
            confirmation_file_content = convert_to_xml(fps_file)
            file_name = fps_file.transaction.transaction_id
            confirmation_xml_file_name = '{0}.xml'.format(file_name)
            confirmation_zip_file_name = '{0}.zip'.format(file_name)
            # 3. Write XML to file
            with open(confirmation_xml_file_name, "w+") as f:
                f.write(confirmation_file_content)
            with zipfile.ZipFile(confirmation_zip_file_name, 'w') as z:
                z.write(confirmation_xml_file_name)
            log_to_console('[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_confirmation"]))
            file_service.upload_file(confirmation_zip_file_name, config["hdfs_files_path_confirmation"])
            log_to_console('[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key))
            hbase_service.update_outgoing_confirmation(fps_file.transaction.row_key, "CONFIRMED_UPLOADED", confirmation_zip_file_name)
            os.remove(confirmation_xml_file_name)
            os.remove(confirmation_zip_file_name)
            kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_CONFIRMED_UPLOADED')
        except Exception as exc:
            log_to_console('Error during processing file: {0}'.format(str(exc)))

    log_to_console('fps-confirmation-file-generator - finished')

#region HDFS


def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        log_to_console('Test active name node : {0}'.format(active_name_node))
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path_confirmation"])
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
    processing_date_short = date.format('YYYYMMDD')
    file_id = processing_date_short + 'A440380S      F000008270'
    submission_id = fps_file.file_id
    amount = fps_file.transaction.amount
    fpid = '00000000798395900150' + processing_date_short + '826200000     '
    processing_time = date.format('HH:mm:ss')
    receiver_branch_code = fps_file.transaction.receiver_sort_code
    receiver_account_number = fps_file.transaction.receiver_account_number
    reference_information = fps_file.transaction.reference
    
    if(len(fps_file.transaction.reference) > 18):
        reference_information = fps_file.transaction.reference[:17].upper()
    else:
        reference_information = fps_file.transaction.reference.upper()
    orig_customer_account_name = fps_file.transaction.sender_name
    
    if(len(fps_file.transaction.sender_name) > 18):
        orig_customer_account_name = fps_file.transaction.sender_name[:17].upper()
    else:
        orig_customer_account_name = fps_file.transaction.sender_name.upper()
    
    xml_converter = xmlConverter.XMLConverter()
    
    if(fps_file.transaction.status == 'CONFIRMED'):
        return xml_converter.convert_confirmed(file_id, processing_date_short, submission_id, amount, fpid, processing_time, receiver_branch_code, receiver_account_number, reference_information, orig_customer_account_name)
    
    return xml_converter.convert_confirmed_failure(file_id, processing_date_short, submission_id, amount, fpid, processing_time, receiver_branch_code, receiver_account_number, reference_information, orig_customer_account_name, fps_file.transaction.rejection_reason)

   
#endregion

#region logging

def log_to_console(message):
    processing_date = datetime.utcnow()
    processing_date_string = str(processing_date)
    print '{0} - {1}'.format(processing_date_string, message)

#endregion

main(sys.argv[1:])
