
import sys
import getopt
import os
import shutil
import logging
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models'))
import transaction
import fpsFile

class CsvParser:

    def parse(self, content):
        lines = content.splitlines()
        fps_file = fpsFile.FpsFile()
        fps_file.transactions = []
        i = 0
        for line in lines:
            if(i == 0):
                fps_file.file_id = line
            else:
                values = line.split(',')
                fps_file.transactions.append(self.parse_transaction(values))
            i = i + 1
        return fps_file

    def parse_transaction(self, values):
        txn = transaction.Transaction()
        txn.nostro_sort_code = values[0]
        txn.nostro_account_number = values[1]
        txn.amount = float(values[2])
        txn.receiver_sort_code = values[3]
        txn.receiver_account_number = values[4]
        txn.receiver_name = values[5]
        txn.reference = values[6]
        txn.sender_name = values[7]
        return txn


