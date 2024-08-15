# mongodb_client.py

import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://badmkavinda:{password}@sensezcluster.esoo75g.mongodb.net/?retryWrites=true&w=majority&appName=SensezCluster"

client = MongoClient(connection_string)
db = client.sensez