import os
from dotenv import load_dotenv

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

#Configuration to grab db details from .env file
load_dotenv()

HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME  = os.getenv('DB_NAME')
# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
    USER, PASSWORD, HOST, DB_NAME
    )
SQLALCHEMY_TRACK_MODIFICATIONS = False





