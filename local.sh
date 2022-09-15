#!/bin/bash
rm -rf dist
python -m build
python -m pip install -e .
