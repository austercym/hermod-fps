
from kafka import KafkaProducer
import time
import avroConverter
import json
import datetime


class KafkaLogger:

    def __init__(self, config):
        self.topic_fps_file_summary = config['topic_fps_file_summary']
        self.topic_fps_hdfs_files_summary = config['topic_fps_hdfs_files_summary']
        bootstrap_servers = config['bootstrap_servers']
        self.avro_writer = avroConverter.AvroConverter(config)
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, api_version=(
            0, 10, 1), security_protocol="SASL_PLAINTEXT", sasl_mechanism='GSSAPI')

    def file_stats(self, file_id, file_type, file_status):
        # print 'File ' + file_type + ' has been processed with status ' + file_status
        fpsFileSummary = FpsFileSummary(file_id, file_type, file_status)
        avro = self.avro_writer.convertFpsFileSummary(fpsFileSummary.toJSON())
        self.producer.send(self.topic_fps_file_summary, avro)
        self.producer.flush()

    def file_hdfs_stats(self, file_count, file_type):
        # print 'Files ' + file_count + ' has been processed with status ' + file_type
        fpsHdfsFilesSummary = FpsHdfsFilesSummary(file_count, file_type)
        avro = self.avro_writer.convertFpsHdfsFilesSummary(fpsHdfsFilesSummary.toJSON())
        self.producer.send(self.topic_fps_hdfs_files_summary, avro)
        self.producer.flush()

class FpsFileSummary:
    def __init__(self, file_id, file_type, file_status):
        self.fileId = file_id
        self.fileStatus = file_status
        self.fileType = file_type
        self.eventType = 'FpsFileSummary'
        self.timestamp = datetime.datetime.now().isoformat()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class FpsHdfsFilesSummary:
    def __init__(self, file_count, file_type):
        self.fileCount = file_count
        self.fileType = file_type
        self.eventType = 'FpsHdfsFilesSummary'
        self.timestamp = datetime.datetime.now().isoformat()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
