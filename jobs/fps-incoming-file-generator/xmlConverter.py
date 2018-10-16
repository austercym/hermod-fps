
import sys
import getopt
import os
import shutil
import logging
import json
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir+'/modules/models'))
import incomingTransaction


class XMLConverter:

    def convert(self, transaction, date, short_date):
        xmlTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.054.001.01" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <BkToCstmrDbtCdtNtfctnV01>
      <GrpHdr>
         <MsgId>%(payment_id)s</MsgId>
         <CreDtTm>%(date)s</CreDtTm>
      </GrpHdr>
      <Ntfctn>
         <Id>%(payment_id)s</Id>
         <CreDtTm>%(date)s</CreDtTm>
         <Acct>
            <Id>
               <PrtryAcct>
                  <Id>%(nostro_sort_code)s</Id>
               </PrtryAcct>
            </Id>
            <Ccy>GBP</Ccy>
         </Acct>
         <TxsSummry>
            <TtlNtries>
               <NbOfNtries>1</NbOfNtries>
               <Sum>%(amount)s</Sum>
            </TtlNtries>
            <TtlCdtNtries>
               <NbOfNtries>1</NbOfNtries>
               <Sum>%(amount)s</Sum>
            </TtlCdtNtries>
            <TtlDbtNtries>
               <NbOfNtries>0</NbOfNtries>
               <Sum>0.00</Sum>
            </TtlDbtNtries>
         </TxsSummry>
         <Ntry>
            <Amt Ccy="GBP">%(amount)s</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <Sts>BOOK</Sts>
            <BookgDt>
               <Dt>%(short_date)s</Dt>
            </BookgDt>
            <BkTxCd>
               <Prtry>
                  <Cd>SIP UKBA CR 40269</Cd>
               </Prtry>
            </BkTxCd>
            <TxDtls>
               <Refs>
                  <EndToEndId>%(payment_id)s</EndToEndId>
                  <TxId>%(payment_id)s</TxId>
               </Refs>
               <RltdPties>
                  <Dbtr>
                     <Nm>%(sender_name)s</Nm>
                  </Dbtr>
                  <DbtrAcct>
                     <Id>
                        <PrtryAcct>
                           <Id>%(sender_account_number)s</Id>
                        </PrtryAcct>
                     </Id>
                  </DbtrAcct>
                  <Cdtr>
                     <Nm>%(receiver_name)s</Nm>
                  </Cdtr>
                  <CdtrAcct>
                     <Id>
                        <PrtryAcct>
                           <Id>%(receiver_account_number)s</Id>
                        </PrtryAcct>
                     </Id>
                  </CdtrAcct>
                  <Prtry>
                     <Tp>IPAGOO - GBP</Tp>
                     <Pty />
                  </Prtry>
               </RltdPties>
               <RmtInf>
                  <Strd>
                     <AddtlRmtInf>NO REF</AddtlRmtInf>
                  </Strd>
                  <Strd>
                     <AddtlRmtInf>%(reference)s</AddtlRmtInf>
                  </Strd>
               </RmtInf>
               <RltdDts>
                  <TxDtTm>%(date)s</TxDtTm>
               </RltdDts>
               <AddtlTxInf>RP46799630545165001020181004826200026</AddtlTxInf>
            </TxDtls>
            <AddtlNtryInf>COMPLETE//0000//001//CREDIT</AddtlNtryInf>
         </Ntry>
      </Ntfctn>
   </BkToCstmrDbtCdtNtfctnV01>
</Document>"""

        data = {'payment_id': transaction.row_key, 'date': date, 'nostro_sort_code': transaction.nostro_sort_code + '' + transaction.nostro_account_number, 
                'amount': "%.2f" % transaction.amount, 'sender_name': transaction.sender_name, 'receiver_name': transaction.receiver_name,
                'short_date': short_date, 'reference': transaction.reference, 'sender_account_number': transaction.sender_sort_code + '' + transaction.sender_account_number,
                'receiver_account_number': transaction.nostro_sort_code + '' + transaction.receiver_account_number, 'reference': transaction.reference}

        #print xmlTemplate % data

        return xmlTemplate % data
