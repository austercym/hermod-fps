import io
import datetime
import uuid
import base64
import avro.schema
from avro.io import DatumWriter
import idGenerator


class AvroConverter:

    def __init__(self, config):
        schema_path = config['schema']
        self.schema = avro.schema.parse(open(schema_path).read())
        self.idGenerator = idGenerator.IdGenerator(config)


    def convertFpsFileSummary(self, json):
        writer = avro.io.DatumWriter(self.schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write({
            "event": {
                "version": "0.0.1",
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "fps.file.processed",
                "name": "FpsFileSummary",
                "parentKey": "",
                "key": "{0}".format(self.idGenerator.generateUniqueId()),
                "data": json
            },
            "processIdentifier": {
                "uuid": "{0}".format(self.idGenerator.generateUniqueId())
            },
            "entityIdentifier": {
                "entity": "IPAGOO",
                "brand": "IPAGOO"
            }
        }, encoder)
        return base64.b64encode(bytes_writer.getvalue())
    
    def convertFpsHdfsFilesSummary(self, json):
        writer = avro.io.DatumWriter(self.schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write({
            "event": {
                "version": "0.0.1",
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "fps.hdfs.files",
                "name": "FpsHdfsFilesSummary",
                "parentKey": "",
                "key": "{0}".format(self.idGenerator.generateUniqueId()),
                "data": json
            },
            "processIdentifier": {
                "uuid": "{0}".format(self.idGenerator.generateUniqueId())
            },
            "entityIdentifier": {
                "entity": "IPAGOO",
                "brand": "IPAGOO"
            }
        }, encoder)
        return base64.b64encode(bytes_writer.getvalue())
