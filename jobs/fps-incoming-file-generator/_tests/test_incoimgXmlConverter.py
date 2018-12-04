import sys
import getopt
import os
import shutil
import logging
import pytest
import json
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../../modules/models'))
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data'))
import incomingTransaction
import incomingXmlConverter

@pytest.fixture
def xml_converter():
    return incomingXmlConverter.XMLConverter()


data = json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/data_correct_xml.json')))


@pytest.mark.parametrize(*data)
def test_incoming_transcations(xml_converter, expected_xml):
    transaction = incomingTransaction.IncomingTransaction()
    transaction.row_key = "434414559091901101"
    transaction.nostro_sort_code = "200023"
    transaction.nostro_account_number = "622398"
    transaction.amount = 0.26
    transaction.receiver_sort_code = "233456"
    transaction.receiver_account_number = "00015051"
    transaction.receiver_name = "CMCoombs Ipagoo"
    transaction.reference = "Cmcoombs hsbc"
    transaction.sender_name = "COOMBS&PERAL"
    transaction.status = "test"
    transaction.sender_account_number = "72550156"
    transaction.sender_sort_code = "400621"
    date = "2018-11-09 19:14:38"
    short_date = "2018-11-09"
    # act
    xml = xml_converter.convert(transaction, date, short_date)
    print xml.lower()
    # assert
    assert expected_xml.strip().lower() == xml.strip().lower()
