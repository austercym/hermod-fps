
import sys
import getopt
import os
import shutil
import logging
import json
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir+'/modules/models'))
import transaction
import fpsFile


class JsonConverter:

    def __init__(self, config):
        self.config = config

    def convert(self, transaction, message_id):
        if(transaction.sender_name.strip().lower() == 'OWELL UNION PARTNE'.strip().lower() or not transaction.sender_name.strip()):
            transaction.sender_name = 'ipagoo LLP'
        
        #TODO: what about the other fields? 
        data = {"paymentType": "SIP",
                "intrBkSttlmAmtCcy": "GBP",
                "intrBkSttlmAmt": transaction.amount,
                "dbtrAgt": self.config['sender_sort_code'],
                "dbtrAcct": self.config['sender_account_number'],
                "dbtrAcctId": "",
                "dbtrNm": transaction.sender_name,
                "endToEndId": message_id,
                "cdtrAgt": transaction.receiver_sort_code,
                "cdtrAcct": transaction.receiver_account_number,
                "cdtrAcctId": "",
                "cdtrNm": transaction.receiver_name,
                "cdtrPstlAdr": [""],
                "ctgyPurp": "",
                "purp": "",
                "returnedPaymentId": "",
                "paymentReturnCode": "",
                "referenceInformation": transaction.reference}
        return json.dumps(data)

