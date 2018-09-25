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
    os.path.realpath(__file__)), os.pardir+'/models'))
sys.path.append(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data'))
import transaction
import fpsFile
import csvParser


@pytest.fixture
def csv_parser():
    return csvParser.CsvParser()


data = json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/data_correct_files.json')))


@pytest.mark.parametrize(*data)
def test_read_transcations(csv_parser, expected_length, content, file_id):
    # act
    fps_file = csv_parser.parse(content)
    transactions = fps_file.transactions

    # assert
    assert int(expected_length) == len(transactions)
    assert file_id == fps_file.file_id
