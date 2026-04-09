# coding=utf-8
import os
import sys
import logging
import socket
from pathlib import Path

LOG_PATH = os.getenv("LOG_PATH") or Path(__file__).absolute().parent / Path("pythonlogs")
