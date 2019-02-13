#!/usr/bin/env bash
rm -rf source/api
sphinx-apidoc -f -H "API Documentation" -A "Sean Mertiens" -V "1.0.0" -o source/api ../src
sphinx-build source/ build/
