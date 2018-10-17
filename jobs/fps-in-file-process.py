import sys
import getopt
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules/models'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fps-in-file-process'))
import apiClient
import idGenerator
import zooconfig
import jsonConverter
import csvParser
import hdfFileService
import hbaseService
import requests
import kafkaLogger
from datetime import datetime, timedelta, time

def main(args):
    print '### fps-in-file-process service - started'
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

    zookeeper_config = '/fps/outgoing/fps-in-file-process/'
    

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config
    
    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    file_service = check_active_name_node(config)
    generator = idGenerator.IdGenerator(config)
    csv_parser = csvParser.CsvParser()
    hbase_service = hbaseService.HbaseService(config)
    kafka_logger = kafkaLogger.KafkaLogger(config)
        
    for file_tuple in get_files(config, file_service):
        message_id = generator.generatePaymentId()
        try:
            file_path = file_tuple[1]
            file_modification_time = file_tuple[2]
            file_id = file_tuple[3]
            print '[Process files] Processing file {0} with id : {1}'.format(file_path,file_id )
            # get the processing date
            processing_date = datetime.utcnow()
            processing_date_string = str(processing_date)
            print '[Process files] Processing date : {0}'.format(processing_date_string)

            # 2. Get file content
            content = file_service.get_file_content(file_path)
            #print '[Process files] Get file content : {0}'.format(content)

            # 3. Parse file content
            fps_file = csv_parser.parse(content)
            if(fps_file != None):
                print '[Process files] Parse file content'

                # 4. Save transaction with status 'NEW' in hbase
                print '[HBase] Save file : {0}'.format(fps_file.file_id)
                fps_file.transaction.row_key = message_id
                fps_file.transaction.status = "NEW"
                kafka_logger.file_stats(message_id, "Outgoing", 'OUTGOING_NEW')
                print '[HBase] Save transaction : {0}'.format(fps_file.transaction.row_key)
                hbase_service.save_message(fps_file.transaction.row_key, fps_file.transaction, processing_date_string, file_path, fps_file.file_id)
                            
                # 5. Call FP API
                token = get_token(config)
                transaction = send_payment(config, fps_file.transaction, token, message_id)

                # 6. Update transaction with status 'ACK' or 'NACK' in hbase
                hbase_service.update_message(fps_file.transaction.row_key, fps_file.transaction)
                
                # 7. Move file to archive in HDFS
                archive_file(config, file_service, file_id, file_path)
                kafka_logger.file_stats(message_id, "Outgoing", 'OUTGOING_{0}'.format(fps_file.transaction.status))
            else:
                set_error_file(config, file_service, file_id, file_path)
                kafka_logger.file_stats(message_id, "Outgoing", 'OUTGOING_ERROR')
        except Exception as exc:
            print '### Error during fp api call:', exc
            print repr(exc)
            set_error_file(config, file_service, file_id, file_path)
            hbase_service.update_message_status(message_id, "ERROR")
            kafka_logger.file_stats(message_id, "Outgoing", 'OUTGOING_ERROR')
                
    print '### fps-in-file-process service - finished'

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

    file_service = hdfFileService.HdfsFileService(config, active_name_node)
    print('### Active name node : ' + active_name_node)
    return file_service

def get_files(config, file_service):
    print '[HDFS Get files] FPS File search : {0}'.format(config["hdfs_files_path"])
    files = file_service.get_files(config["hdfs_files_path"])
    print '[HDFS Get files] Found {0} new file(s)'.format(len(files))
    files_to_process = [(f, '%s/%s' % (config["hdfs_files_path"], f), str(file_status['modificationTime']),
                       str(file_status['modificationTime']) + '.' + f) for f, file_status in files]
    return files_to_process

def archive_file(config, file_service, file_id, file_path):
    print '[HDFS Archive file] Move file to archive : {0}'.format(config["hdfs_archive_folder"])
    file_service.archive(file_id, file_path)


def set_error_file(config, file_service, file_id, file_path):
    print '[HDFS Archive file] Move file to archive : {0}'.format(config["hdfs_archive_folder"])
    file_service.set_error_file(file_id, file_path)

#endregion

#region JSON CONVERTER

def parse_transaction(config, transaction, message_id):
    # Transform CSV -> JSON
    json_converter = jsonConverter.JsonConverter(config)
    transaction_json = json_converter.convert(transaction, message_id)
    #print '[Process files] Convert csv to json : {0}'.format(transaction_json)
    return transaction_json

#endregion

#region API

def get_token(config):
    api_client = apiClient.ApiClient(config)

    print '[API Get Token] Send request to get token'
    response = api_client.get_token()
    
    if(response.status_code == requests.codes.ok):
        response_json = response.json()
        #print '[API Get Token] Response recived from api : {}'.format(response_json)
        return response_json['access_token']

    raise Exception('API Get Token response code {0}'.format(response.status_code))

def send_payment(config, transaction, token, message_id):
    api_client = apiClient.ApiClient(config)
    print '[API Send Payment] Send payment request'   
    response = api_client.send_payment(token, parse_transaction(config, transaction, message_id))
    if(response.status_code == requests.codes.ok):
        #get the json response
        response_json = response.json()
        #print '[API Send Payment] Response recived from api : {}'.format(response_json)

        # Check payment status if SENT than status = ACK if RJCT status = NACK
        if(response_json['txSts'] == 'SENT'):
            transaction.status = "ACK"
        else:
            transaction.status = "NACK"

        #Set returned payment id as transaction id    
        transaction.transaction_id = response_json['paymentId']
        return transaction
    else:
        print '[API Send Payment] response {0}'.format(response.json())
        
    raise Exception('API Get Token response code {0}'.format(response.status_code))

#endregion



main(sys.argv[1:])
