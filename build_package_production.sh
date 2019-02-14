#!/usr/bin/env bash
rm dist/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*

# cleanup
rm -rf build
rm -rf src/atraxi_flow.egg-info/
