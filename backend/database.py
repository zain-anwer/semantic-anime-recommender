from pymongo import MongoClient
from dotenv import load_dotenv
import os                           # we need the os library to read the env file

# the equivalent of dotenv.config() perhaps
# so that we could load environment variables
load_dotenv()

client = MongoClient(os.getenv('DB_URI'))
db = client[os.getenv('DB_NAME')]
anime_collection = db['anime']
query_cache = db['query_cache']