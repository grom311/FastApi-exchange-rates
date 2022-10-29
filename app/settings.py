import os

from dotenv import load_dotenv

load_dotenv()

# redis
REDIS_HOST = os.environ.get("REDIS_HOST", 'localhost')
REDIS_PORT = os.environ.get("REDIS_PORT", '6379')

RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME", 'admin')
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", 'admin')
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", 'localhost')