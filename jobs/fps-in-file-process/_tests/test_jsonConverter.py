# import sys
# import getopt
# import os
# import shutil
# import logging
# import pytest
# import json
# sys.path.append(os.path.join(os.path.dirname(
#     os.path.realpath(__file__)), os.pardir))
# sys.path.append(os.path.join(os.path.dirname(
#     os.path.realpath(__file__)), '../../modules/models'))
# sys.path.append(os.path.join(os.path.dirname(
#     os.path.abspath(__file__)), 'data'))
# import transaction
# import fpsFile
# import csvParser
# import jsonConverter

# @pytest.fixture
# def csv_parser():
#     return csvParser.CsvParser()

# @pytest.fixture
# def json_converter():
#     return jsonConverter.JsonConverter()

# data = json.load(open(os.path.join(os.path.dirname(
#     os.path.abspath(__file__)), 'data/data_correct_json.json')))


# @pytest.mark.parametrize(*data)
# def test_read_transcations(csv_parser, json_converter, expected_json, content):
#     # act
#     fps_file = csv_parser.parse(content)
#     transaction = fps_file.transaction
#     transactionJson = json_converter.convert(transaction, None)
#     print transactionJson
#     # assert
#     assert transactionJson == expected_json
