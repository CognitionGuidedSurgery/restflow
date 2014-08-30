#!/bin/bash
export PYTHONPATH=/homes/students/weigl/.local/lib/python2.7/site-packages
export LD_LIBRARY_PATH=/homes/students/weigl/.local/lib/
gunicorn -D -w 4 -b 0.0.0.0:8002 restflow.server:app
