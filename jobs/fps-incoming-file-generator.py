import sys
import getopt
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'modules'))
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'fps-incoming-file-generator'))
import zooconfig
import hdfFileService
import hbaseService
import incomingXmlConverter
import arrow
import kafkaLogger

def main(args):
    print '### fps-incoming-file-generator - started'
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

    zookeeper_config = '/fps/incoming/fps-incoming-file-generator/'

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config
    

    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    file_service = check_active_name_node(config)
    hbase_service = hbaseService.HbaseService(config)
    kafka_logger = kafkaLogger.KafkaLogger(config)

    # 1. Get transaction from hbase
    transactions = hbase_service.get_incoming_messages()
    for transaction in transactions:
        try:
            # 2. Convert to XML
            kafka_logger.file_stats(transaction.row_key, "Incoming", 'INCOMING_NEW')
            incoming_file_content = convert_to_xml(transaction)
            print '[XML] Converted xml : {0}'.format(incoming_file_content)
            incoming_file_name = 'FPS_{0}.xml'.format(transaction.row_key)
            # 3. Write XML to file
            with open(incoming_file_name, "w+") as f:
                f.write(incoming_file_content)
            
            # 4. Upload file to HDFS
            print '[HDFS upload file] Upload generated file to HDFS : {0}'.format(config["hdfs_files_path_incoming"])
            file_service.upload_file(incoming_file_name, config["hdfs_files_path_incoming"])
            # 5. Update status in Hbase
            print '[Hbase row_key ]  {0}'.format(transaction.row_key)
            hbase_service.update_incoming_message_status(transaction.row_key, "INCOMING_UPLOADED")
            # 6. Remove temp file
            os.remove(incoming_file_name)
            # 7. Log to kafka
            kafka_logger.file_stats(transaction.row_key, "Incoming", 'INCOMING_UPLOADED')
        except Exception as exc:
            # TODO: [Exception] Log to kafka ??
            # kafka_logger.file_stats(incoming_file_name, "Incoming", 'INCOMING_ERROR')
            print '### Error during creating incoming file:', exc
            print repr(exc)

    print '### fps-incoming-file-generator - finished'

#region HDFS


def check_active_name_node(config):
    active_name_node = config['hdfs_name_node_1']

    try:
        print('### Test active name node : ' + active_name_node)
        file_service = hdfFileService.HdfsFileService(config, active_name_node)
        file_service.get_files(config["hdfs_files_path_incoming"])
    except Exception as exc:
        print('### Name node : ' + active_name_node + ' is not active!')
        active_name_node = config['hdfs_name_node_2']

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    print('### Active name node : ' + active_name_node)
    return file_service

#endregion

#region convert to xml


def convert_to_xml(transaction):
    print '[XML] Convert model to XML'
    date = arrow.utcnow()
    date_long = date.format('YYYY-MM-DD HH:mm:ss')
    short_date = date.format('YYYY-MM-DD')
    xml_converter = incomingXmlConverter.XMLConverter()
    return xml_converter.convert(transaction, date_long, short_date)

#endregion

main(sys.argv[1:])
