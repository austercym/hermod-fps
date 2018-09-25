
import sys
import getopt
import os
import shutil
import logging
import json
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'models'))
import transaction
import fpsFile


class JsonConverter:

    def convert(self, transaction):
        #TODO: what about the other fields? 
        data = {"paymentType": "SIP",
                "intrBkSttlmAmtCcy": "GBP",
                "intrBkSttlmAmt": transaction.amount,
                "dbtrAgt": "235889",
                "dbtrAcct": "89989983",
                "dbtrAcctId": "650042IPAGO",
                "dbtrNm": transaction.sender_name,
                "endToEndId": transaction.transaction_id,
                "cdtrAgt": transaction.receiver_sort_code,
                "cdtrAcct": "23000032",
                "cdtrAcctId": "",
                "cdtrNm": transaction.receiver_name,
                "cdtrPstlAdr": ["123 NOWHERE ROAD","CAMBRIDGE"],
                "ctgyPurp": "INTERNET",
                "purp": "BIL",
                "returnedPaymentId": "",
                "paymentReturnCode": "",
                "referenceInformation": transaction.reference}
        return json.dumps(data)

