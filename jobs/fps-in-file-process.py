import sys
import getopt
import os
import shutil
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fps-in-file-process'))
import apiClient
import idGenerator
import zooconfig
import jsonConverter
import csvParser
import hdfFileService
import hbaseService

def main(args):
    print '### fps-in-file-process service - started'
    get zookeeper url from arguments
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

    zookeeper_config = '/fps/incoming/fps-in-file-process/'
    

    print '### Fetching configuration from zookeeper url: ', zookeeper_url
    print '### Fetching configuration from zookeeper node: ', zookeeper_config
    
    # 0. Init
    config = zooconfig.get_config(zookeeper_url, zookeeper_config)
    generator = idGenerator.IdGenerator(config)
    api_client = apiClient.ApiClient(config)
    csv_parser = csvParser.CsvParser()
    json_converter = jsonConverter.JsonConverter()
    file_service = hdfFileService.HdfsFileService(config, active_node)
    hbase_service = hbaseService.HbaseService(config)

    # 1. Get files from HDFS 
    print '[HDFS Get files] FPS File search : {0}'.format(config["hdfs_files_path"])
    files = file_service.get_files(config["hdfs_files_path"])
    print '[HDFS Get files] Found {0} new file(s)'.format(len(files))
    filesToProcess = [(f, '%s/%s' % (self.filesPath, f), str(file_status['modificationTime']),
                       str(file_status['modificationTime']) + '.' + f) for f, file_status in files]
    for fileTuple in filesToProcess:
        file_path = fileTuple[1]
        file_modification_time = fileTuple[2]
        file_id = fileTuple[3]
        print '[Process files] Processing file {0} with id : {1}'.format(file_path,file_id )
        # get the processing date
        processing_date = datetime.utcnow()
        processing_date_string = str(processing_date)
        print '[Process files] Processing date : {0}'.format(processing_date_string)
        # 2. Get file content
        content = self.fileService.get_file_content(file_path)
        print '[Process files] Get file content : {0}'.format(content)
        # 3. Parse file content
        fps_file = parser.parse(content)
        print '[Process files] Parse file content'
        # 3. Save transaction with status 'NEW' in hbase
        print '[HBase] Save file : {0}'.format(fps_file.file_id)
        hbase_service.saveFile(fps_file.file_id, file_path, content, "", fps_file.transactions[0], "NEW", processing_date_string, processing_date_string)
        
        # 4. Transform CSV -> JSON
        transactionJson = converter.convert(fps_file.transactions[0])
        print '[Process files] Convert csv to json : {0}'.format(transactionJson)
        # 5. Call FP API
        try:
            response = api_client.get_token()
            print '[API Get Token] Response recived from api : {}'.format(response.json())
            response2 = api_client.send_payment(response['access_token'])
            print '[API Send Payment] Response recived from api : {}'.format(response2.json())
        except Exception as exc:
            print '### Error during fp api call:', exc
            print repr(exc)

        # 6. Update transaction with status 'ACK' or 'NACK' in hbase

        # 7. Move file to archive in HDFS

    print '### fps-in-file-process service - finished'


main(sys.argv[1:])
