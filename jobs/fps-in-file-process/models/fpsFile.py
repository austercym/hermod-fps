import sys
import getopt
import os
import shutil
import logging
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'models'))
import transaction

class FpsFile:
    
    def __init__(self, file_id=None, file_name=None, file_content=None, transactions=[]):
        self._file_id = file_id
        self._file_name = file_name
        self._file_content = file_content
        self._transactions = transactions
    
    @property
    def file_id(self):
        return self._file_id

    @file_id.setter
    def file_id(self, value):
        self._file_id = value

    @property
    def transactions(self):
        return self._transactions

    @transactions.setter
    def transactions(self, value):
        self._transactions = value
