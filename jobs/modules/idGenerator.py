# from networkclient import IdGeneratorCommandProducer
import traceback
import uuid


class IdGenerator:

    def __init__(self, config):
        self.config = config
        port = int(config['idGeneratorPort'])
        self.idGenerator = IdGeneratorCommandProducer(port)

    def generateUniqueId(self, count=None):
        id = self.idGenerator.getGeneralUniqueId(1)[0]
        #id = str(uuid.uuid4())[:32]
        return id

    def generatePaymentId(self, count=None):
        id = self.idGenerator.getFasterPaymentUniqueId(1)[0]
        #id = str(uuid.uuid4())[:32]
        return id
