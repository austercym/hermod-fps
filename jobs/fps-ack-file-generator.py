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

def main(args):
    print '### fps-ack-file-generator - started'
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

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config

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

                print '[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_ack"])
                file_service.upload_file(ack_file_name, config["hdfs_files_path_ack"])
                # 5. Update status in Hbase
                print '[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key)
                hbase_service.update_message_status(fps_file.transaction.row_key, "ACK_UPLOADED")
                # 7. Log to kafka
                kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_ACK_UPLOADED')
            elif(fps_file.transaction.status == 'NACK'):

                print '[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_nack"])
                print '[Hbase row_key ]  {0}'.format(fps_file.transaction.row_key)
                file_service.upload_file(ack_file_name, config["hdfs_files_path_nack"])
                # 5. Update status in Hbase
                hbase_service.update_message_status(fps_file.transaction.row_key, "NACK_UPLOADED")
                # 7. Log to kafka
                kafka_logger.file_stats(fps_file.transaction.transaction_id, "Outgoing", 'OUTGOING_NACK_UPLOADED')
            os.remove(ack_file_name)
        except Exception as exc:
            print '### Error during creating ack file:', exc
            print repr(exc)

    print '### fps-ack-file-generator - finished'

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

main(sys.argv[1:])
