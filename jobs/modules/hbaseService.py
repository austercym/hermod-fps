import sys
import getopt
import os
import shutil
import logging
from pyspark import SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import *
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'models'))
import transaction
import fpsFile
import incomingTransaction

class HbaseService:

    def __init__(self, config):
        self.config = config
        self.fps_messages_table = config["fps_messages_table"]
        self.fps_incoming_messages_table = config["fps_incoming_messages_table"]
        self.phoenix_url = config['phoenix_url']
        self.sc = SparkContext()

    def save_message(self, row_key, transaction, created, transaction_file_name, file_id):
        dataSet = []
        dataSet.append((row_key, transaction.nostro_sort_code, transaction.nostro_account_number, transaction.amount, transaction.receiver_sort_code, transaction.receiver_account_number, transaction.receiver_name, transaction.reference, transaction.sender_name,
                        transaction.status, created, transaction_file_name, None, None, None, file_id))
        
        rdd = self.sc.parallelize(dataSet)

        schema = StructType([
            StructField("ROWKEY", StringType(), True),
            StructField("NOSTRO_SORT_CODE", StringType(), True),
            StructField("NOSTRO_ACCOUNT_NUMBER", StringType(), True),
            StructField("AMOUNT", FloatType(), True),
            StructField("RECEIVER_SORT_CODE", StringType(), True),
            StructField("RECEIVER_ACCOUNT_NUMBER", StringType(), True),
            StructField("RECEIVER_NAME", StringType(), True),
            StructField("REFERENCE", StringType(), True),
            StructField("SENDER_NAME", StringType(), True),
            StructField("STATUS", StringType(), True),
            StructField("CREATED", StringType(), True),
            StructField("TRANSACTION_FILE_NAME", StringType(), True),
            StructField("ACK_FILE_NAME", StringType(), True),
            StructField("CONFIRMATION_FILE_NAME", StringType(), True),
            StructField("PAYMENT_ID", StringType(), True),
            StructField("TRANSACTION_FILE_ID", StringType(), True)
        ])
        

        sqlc = SQLContext(self.sc)
        df = sqlc.createDataFrame(rdd, schema=schema)

        df.write.format("org.apache.phoenix.spark").mode("overwrite").option(
            "table", '"' + self.fps_messages_table + '"').option("zkUrl", self.phoenix_url).save()

    def update_message(self, row_key, transaction):
        rdd = self.sc.parallelize([(row_key, transaction.transaction_id, transaction.status)])
        df = rdd.toDF(["ROWKEY", "PAYMENT_ID", "STATUS"])
        df.write.format("org.apache.phoenix.spark").mode("overwrite").option(
            "table", '"' + self.fps_messages_table + '"').option("zkUrl", self.phoenix_url).save()
    
    def update_message_status(self, row_key, status):
        rdd = self.sc.parallelize([(row_key, status)])
        df = rdd.toDF(["ROWKEY", "STATUS"])
        df.write.format("org.apache.phoenix.spark").mode("overwrite").option(
            "table", '"' + self.fps_messages_table + '"').option("zkUrl", self.phoenix_url).save()

    def get_ack_messages(self):
        fps_files = []

        sqlc = SQLContext(self.sc)
        df = sqlc.read \
            .format("org.apache.phoenix.spark") \
            .option("table", '"' + self.fps_messages_table + '"') \
            .option("zkUrl", self.phoenix_url) \
            .load()
        df.registerTempTable("hbasetable")
        query = 'SELECT ROWKEY, NOSTRO_SORT_CODE, NOSTRO_ACCOUNT_NUMBER, AMOUNT, RECEIVER_SORT_CODE, RECEIVER_ACCOUNT_NUMBER, RECEIVER_NAME, REFERENCE, SENDER_NAME, STATUS, PAYMENT_ID, TRANSACTION_FILE_NAME, TRANSACTION_FILE_ID FROM hbasetable WHERE STATUS = \'{0}\' OR STATUS = \'{1}\''.format(
            'ACK', 'NACK')
        rowList = sqlc.sql(query).collect()
        for row in rowList:
            fps_file = fpsFile.FpsFile()
            fps_file.file_id = row['TRANSACTION_FILE_ID']
            fps_file.file_name = row['TRANSACTION_FILE_NAME']
            fps_file.transaction = transaction.Transaction()
            fps_file.transaction.row_key = row['ROWKEY']
            fps_file.transaction.nostro_sort_code = row['NOSTRO_SORT_CODE']
            fps_file.transaction.nostro_account_number = row['NOSTRO_ACCOUNT_NUMBER']
            fps_file.transaction.amount = row['AMOUNT']
            fps_file.transaction.receiver_sort_code = row['RECEIVER_SORT_CODE']
            fps_file.transaction.receiver_account_number = row['RECEIVER_ACCOUNT_NUMBER']
            fps_file.transaction.receiver_name = row['RECEIVER_NAME']
            fps_file.transaction.reference = row['REFERENCE']
            fps_file.transaction.sender_name = row['SENDER_NAME']
            fps_file.transaction.status = row['STATUS']
            fps_file.transaction.transaction_id = row['PAYMENT_ID']
            fps_files.append(fps_file)
        return fps_files
    
    def get_incoming_messages(self):
        transactions = []

        sqlc = SQLContext(self.sc)
        df = sqlc.read \
            .format("org.apache.phoenix.spark") \
            .option("table", '"' + self.fps_incoming_messages_table + '"') \
            .option("zkUrl", self.phoenix_url) \
            .load()
        df.registerTempTable("hbasetable")
        query = 'SELECT ROWKEY, NOSTRO_SORT_CODE, NOSTRO_ACCOUNT_NUMBER, AMOUNT, RECEIVER_SORT_CODE, RECEIVER_ACCOUNT_NUMBER, RECEIVER_NAME, REFERENCE, SENDER_NAME, STATUS, SENDER_ACCOUNT_NUMBER, SENDER_SORT_CODE FROM hbasetable WHERE STATUS = \'{0}\''.format(
            'NEW')
        rowList = sqlc.sql(query).collect()
        for row in rowList:
            transaction = incomingTransaction.IncomingTransaction()
            transaction.row_key = row['ROWKEY']
            transaction.nostro_sort_code = row['NOSTRO_SORT_CODE']
            transaction.nostro_account_number = row['NOSTRO_ACCOUNT_NUMBER']
            transaction.amount = row['AMOUNT']
            transaction.receiver_sort_code = row['RECEIVER_SORT_CODE']
            transaction.receiver_account_number = row['RECEIVER_ACCOUNT_NUMBER']
            transaction.receiver_name = row['RECEIVER_NAME']
            transaction.reference = row['REFERENCE']
            transaction.sender_name = row['SENDER_NAME']
            transaction.sender_account_number = row['SENDER_ACCOUNT_NUMBER']
            transaction.sender_sort_code = row['SENDER_SORT_CODE']
            transaction.status = row['STATUS']
            transactions.append(transaction)
        return transactions
    
    def update_incoming_message_status(self, row_key, status):
        rdd = self.sc.parallelize([(row_key, status)])
        df = rdd.toDF(["ROWKEY", "STATUS"])
        df.write.format("org.apache.phoenix.spark").mode("overwrite").option(
            "table", '"' + self.fps_incoming_messages_table + '"').option("zkUrl", self.phoenix_url).save()

    def get_confirmation_messages(self):
        fps_files = []

        sqlc = SQLContext(self.sc)
        df = sqlc.read \
            .format("org.apache.phoenix.spark") \
            .option("table", '"' + self.fps_messages_table + '"') \
            .option("zkUrl", self.phoenix_url) \
            .load()
        df.registerTempTable("hbasetable")
        query = 'SELECT ROWKEY, NOSTRO_SORT_CODE, NOSTRO_ACCOUNT_NUMBER, AMOUNT, RECEIVER_SORT_CODE, RECEIVER_ACCOUNT_NUMBER, RECEIVER_NAME, REFERENCE, SENDER_NAME, STATUS, PAYMENT_ID, TRANSACTION_FILE_NAME, TRANSACTION_FILE_ID, REJECTION_REASON FROM hbasetable WHERE STATUS = \'{0}\' OR STATUS = \'{1}\''.format(
            'CONFIRMED', 'CONFIRMED_REJECTION')
        rowList = sqlc.sql(query).collect()
        for row in rowList:
            fps_file = fpsFile.FpsFile()
            fps_file.file_id = row['TRANSACTION_FILE_ID']
            fps_file.file_name = row['TRANSACTION_FILE_NAME']
            fps_file.transaction = transaction.Transaction()
            fps_file.transaction.row_key = row['ROWKEY']
            fps_file.transaction.nostro_sort_code = row['NOSTRO_SORT_CODE']
            fps_file.transaction.nostro_account_number = row['NOSTRO_ACCOUNT_NUMBER']
            fps_file.transaction.amount = row['AMOUNT']
            fps_file.transaction.receiver_sort_code = row['RECEIVER_SORT_CODE']
            fps_file.transaction.receiver_account_number = row['RECEIVER_ACCOUNT_NUMBER']
            fps_file.transaction.receiver_name = row['RECEIVER_NAME']
            fps_file.transaction.reference = row['REFERENCE']
            fps_file.transaction.sender_name = row['SENDER_NAME']
            fps_file.transaction.status = row['STATUS']
            fps_file.transaction.transaction_id = row['PAYMENT_ID']
            fps_file.transaction.rejection_reason = row['REJECTION_REASON']
            fps_files.append(fps_file)
        return fps_files
