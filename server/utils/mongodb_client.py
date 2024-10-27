# mongodb_client.py

import json
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from langchain.schema import Document

load_dotenv()

password = os.getenv("MONGODB_PWD")
connection_string = f"mongodb+srv://badmkavinda:{password}@sensezcluster.esoo75g.mongodb.net/?retryWrites=true&w=majority&appName=SensezCluster"

# Create a new client and connect to the server
client = MongoClient(
    connection_string, 
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True
)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Connection error: {e}")

db = client.sensez

def get_user_details(username):
    try:
        user_details = db.senceez_user_collection.find_one({"username": username})
        if user_details:
            # Convert ObjectId to string
            user_details['_id'] = str(user_details['_id'])
            return user_details
        else:
            return {"error": "User not found"}
    except PyMongoError as e:
        return {"error": str(e)}
    

def custom_mongodb_loader(connection_string, db_name, collection_name, filter_criteria):
    client = MongoClient(connection_string)
    db = client[db_name]
    collection = db[collection_name]
    documents = collection.find(filter_criteria)
    return [Document(page_content=str(doc)) for doc in documents]