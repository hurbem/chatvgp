#!/bin/bash
set -e
apt-get update
apt-get install -y build-essential libpq-dev python3-dev
pip install --upgrade pip setuptools wheel maturin

pip install -r requirements.txt
