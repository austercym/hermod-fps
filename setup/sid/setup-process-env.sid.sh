#!/bin/bash
pip install virtualenv
virtualenv ./setup-process-env
cd setup-process-env
. ./bin/activate
pip install requests
