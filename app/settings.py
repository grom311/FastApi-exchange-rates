import os

from dotenv import load_dotenv

load_dotenv()

# redis
REDIS_HOST = os.environ.get("REDIS_HOST", 'localhost')
REDIS_PORT = os.environ.get("REDIS_PORT", '6379')