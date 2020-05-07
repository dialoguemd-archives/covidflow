#!/bin/bash
SUITE=$1
shift
exec locust -f load_tests/${SUITE}_locustfile.py "$@"
