import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(join(dirname(__file__), '.env'))
USER_NAME = os.environ.get('USER_NAME')
b = os.environ.get('b')
rk = os.environ.get('rk')
