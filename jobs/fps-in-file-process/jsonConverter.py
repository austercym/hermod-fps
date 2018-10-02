
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

    def convert(self, transaction, message_id):
        #TODO: what about the other fields? 
        data = {"paymentType": "SIP",
                "intrBkSttlmAmtCcy": "GBP",
                "intrBkSttlmAmt": transaction.amount,
                "dbtrAgt": "235889",
                "dbtrAcct": "89989983",
                "dbtrAcctId": "650101IPAGO",
                "dbtrNm": transaction.sender_name,
                "endToEndId": message_id,
                "cdtrAgt": transaction.receiver_sort_code,
                "cdtrAcct": "10000568",
                "cdtrAcctId": "",
                "cdtrNm": transaction.receiver_name,
                "cdtrPstlAdr": [""],
                "ctgyPurp": "INTERNET",
                "purp": "BIL",
                "returnedPaymentId": "",
                "paymentReturnCode": "",
                "referenceInformation": transaction.reference}
        return json.dumps(data)

