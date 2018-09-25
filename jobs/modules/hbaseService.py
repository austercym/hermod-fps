from pyspark import SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import *
import bacsMessage


class HbaseService:

    def __init__(self, config):
        self.config = config
        self.fps_messages_table = config["fps_messages_table"]
        self.phoenix_url = config['phoenix_url']
        self.sc = SparkContext()

    def saveFile(self, row_key, file_name, file_content, orignal_transaction, transaction, status, created, last_update):
        dataSet = []
        dataSet.append((row_key, file_name, file_content, orignal_transaction, transaction.nostro_sort_code, transaction.nostro_account_number, transaction.amount, transaction.receiver_sort_code, ransaction.receiver_account_number, transaction.receiver_name, transaction.reference, transaction.sender_name,
                        status, created, last_update))
        
        rdd = self.sc.parallelize(dataSet)

        schema = StructType([
            StructField("ROWKEY", StringType(), True),
            StructField("FILE_NAME", StringType(), True),
            StructField("FILE_CONTENT", StringType(), True),
            StructField("ORIGNAL_TRANSACTION", StringType(), True),
            StructField("NOSTRO_SORT_CODE", StringType(), True),
            StructField("NOSTRO_ACCOUNT_NUMBER", StringType(), True),
            StructField("AMOUNT", StringType(), True),
            StructField("RECEIVER_SORT_CODE", StringType(), True),
            StructField("RECEIVER_ACCOUNT_NUMBER", StringType(), True),
            StructField("RECEIVER_NAME", StringType(), True),
            StructField("REFERENCE", StringType(), True),
            StructField("SENDER_NAME", StringType(), True),
            StructField("STATUS", StringType(), True),
            StructField("PAYMENT_ID", StringType(), True),
            StructField("CREATED", StringType(), True),
            StructField("LAST_UPDATE", StringType(), True)
        ])

        sqlc = SQLContext(self.sc)
        df = sqlc.createDataFrame(rdd, schema=schema)

        df.write.format("org.apache.phoenix.spark").mode("overwrite").option(
            "table", '"' + self.fps_messages_table + '"').option("zkUrl", self.phoenix_url).save()

    def updateBacsMessageStatus(self, row_key, status):
        rdd = self.sc.parallelize([(transaction_id, status)])
        df = rdd.toDF(["ROWKEY", "STATUS"])
        df.write.format("org.apache.phoenix.spark").mode("overwrite").option(
            "table", '"' + self.fps_messages_table + '"').option("zkUrl", self.phoenix_url).save()
