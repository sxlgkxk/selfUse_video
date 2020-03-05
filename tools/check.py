#!/usr/bin/python3
import sys
import os

folder=sys.argv[1]
if not os.path.exists(folder):
    os.makedirs(folder)