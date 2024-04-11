import os
import sys

# Global settings
DEBUG = True
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.executable), os.pardir)) if not DEBUG \
           else os.path.abspath(os.path.join(os.path.dirname(sys.executable), os.pardir, os.pardir))

# Database settings

DATABASE_PATH = f'{MAIN_DIR}/resources/mediaPlayer.db'

# Client settings

CONFIG_PATH = f'{MAIN_DIR}/resources/config.json'
IMG_DIR = f'{MAIN_DIR}/resources/img'
