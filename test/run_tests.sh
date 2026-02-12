#!/bin/bash
set -e

cd /kb/module

echo "Running Python tests with nose"
python -m nose -v
