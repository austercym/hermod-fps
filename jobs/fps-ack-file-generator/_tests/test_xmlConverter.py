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
import transaction
import fpsFile
import xmlConverter


@pytest.fixture
def xml_converter():
    return xmlConverter.XMLConverter()


data = json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/data_correct_xml.json')))


@pytest.mark.parametrize(*data)
def test_read_transcations(xml_converter, expected_xml, transaction_id, file_id, date, string_date, amount):
    fps_file = fpsFile.FpsFile()
    fps_file.file_id = file_id
    fps_file.transaction = transaction.Transaction()
    fps_file.transaction.transaction_id = transaction_id
    fps_file.transaction.amount = amount
    # act
    xml = xml_converter.convert(fps_file, date, string_date, "complete")
    print xml.lower()
    # assert
    assert expected_xml.strip().lower() == xml.strip().lower()
