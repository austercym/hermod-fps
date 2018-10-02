
import sys
import getopt
import os
import shutil
import logging
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir+'/modules/models'))
import transaction
import fpsFile

class CsvParser:

    def parse(self, content):
        lines = content.splitlines()
        fps_file = fpsFile.FpsFile()
        i = 0
        
        if(len(lines) > 2):
            raise Exception('File contains more than 1 transaction!')

        for line in lines:
            if(i == 0):
                fps_file.file_id = line
            else:
                if(line and line.strip()):
                    values = line.split(',')
                    fps_file.transaction = self.parse_transaction(values)
            i = i + 1

        return fps_file

    def parse_transaction(self, values):
        print 'Transaction line len: {0}'.format(len(values))
        if(len(values) > 6):
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
        raise Exception('Transaction line is to short!')

