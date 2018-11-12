
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


class XMLConverter:

    def convert(self, fps_file, date, string_date, status):
        xmlTemplate = """<?xml version="1.0" encoding="UTF-8"?><SubmitResponse><ResponseHeader xmlns="http://bacs.co.uk/submissions" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0"><ResponseCode>T200</ResponseCode><SubmissionIdentifier>%(payment_id)s</SubmissionIdentifier></ResponseHeader><SubmissionResults xmlns="http://bacs.co.uk/submissions" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" submissionIdentifier="%(payment_id)s" status="%(status)s" submissionType="live" submissionSerialNumber="%(file_id)s" submissionDateAndTime="%(date)s" submissionEarliestDate="%(string_date)s"><SubmittingServiceUser userNumber="440380" name="Ipagoo LLP" /><SubmittingContact contactIdentifier="HSM1077747" fullName="Orwell Union HSM1" /><SigningContact contactIdentifier="HSM1077747" fullName="Orwell Union HSM1" /><PaymentFile status="%(status)s" index="1" paymentFileIdentifier="270" processingDay="%(string_date)s" currency="GBP" creditRecordCount="1" creditValueTotal="%(amount)s" debitRecordCount="0" debitValueTotal="0" workCode="2 FPS    "><OriginatingServiceUser userNumber="440380" name="Ipagoo LLP" /></PaymentFile></SubmissionResults></SubmitResponse>"""
        amount = (float(fps_file.transaction.amount)*100)
        data = {'payment_id': fps_file.transaction.transaction_id, 'file_id': fps_file.file_id,
                'date': date, 'string_date': string_date, 'amount': "%.0f" % amount, 'status': status}

        #print xmlTemplate % data

        return xmlTemplate % data
