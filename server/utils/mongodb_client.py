# mongodb_client.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()  # Load environment variables from .env file

password = os.environ.get("MONGODB_PWD")
if not password:
    raise ValueError("MONGODB_PWD environment variable is not set.")

connection_string = f"mongodb+srv://badmkavinda:{password}@sensezcluster.esoo75g.mongodb.net/?retryWrites=true&w=majority&appName=SensezCluster"

client = MongoClient(connection_string)
db = client.sensez
