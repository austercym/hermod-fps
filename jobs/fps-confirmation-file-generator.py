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

def main(args):
    print '### fps-confirmation-file-generator - started'
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

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config

    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    file_service = check_active_name_node(config)
    hbase_service = hbaseService.HbaseService(config)
    kafka_logger = kafkaLogger.KafkaLogger(config)
    # 1. Get transaction from hbase
    fps_files = hbase_service.get_confirmation_messages()
    for fps_file in fps_files:
        try:
            # 2. Convert to XML
            kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_CONFIRMED')
            confirmation_file_content = convert_to_xml(fps_file)
            print '[XML] Converted xml : {0}'.format(confirmation_file_content)
            file_name = fps_file.transaction.transaction_id
            confirmation_xml_file_name = '{0}.xml'.format(file_name)
            confirmation_zip_file_name = '{0}.zip'.format(file_name)
            # 3. Write XML to file
            with open(confirmation_xml_file_name, "w+") as f:
                f.write(confirmation_file_content)
            with zipfile.ZipFile(confirmation_zip_file_name, 'w') as z:
                z.write(confirmation_xml_file_name)
            print '[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_confirmation"])
            file_service.upload_file(confirmation_zip_file_name, config["hdfs_files_path_confirmation"])
            print '[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key)
            hbase_service.update_message_status(fps_file.transaction.row_key, "CONFIRMED_UPLOADED")
            os.remove(confirmation_xml_file_name)
            os.remove(confirmation_zip_file_name)
            kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_CONFIRMED_UPLOADED')
        except Exception as exc:
            print '### Error during creating ack file:', exc
            print repr(exc)

    print '### fps-confirmation-file-generator - finished'

#region HDFS

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

#endregion

#region convert to xml

def convert_to_xml(fps_file):
    print '[XML] Convert model to XML'
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

main(sys.argv[1:])
