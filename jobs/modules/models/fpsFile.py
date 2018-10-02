import sys
import getopt
import os
import shutil
import logging
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'models'))
import transaction

class FpsFile:
    
    def __init__(self, file_id=None, file_name=None, transaction=None):
        self._file_id = file_id
        self._file_name = file_name
        self._transaction = transaction
    
    @property
    def file_id(self):
        return self._file_id

    @file_id.setter
    def file_id(self, value):
        self._file_id = value
    
    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def transaction(self):
        return self._transaction

    @transaction.setter
    def transaction(self, value):
        self._transaction = value
