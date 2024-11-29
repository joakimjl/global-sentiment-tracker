import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
CONNECT_IP_REMOTE = os.environ.get("CONNECT_IP_REMOTE")
CONNECT_PORT_REMOTE = os.environ.get("CONNECT_PORT_REMOTE")
