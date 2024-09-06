# mongodb_client.py

import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from langchain_community.document_loaders.mongodb import MongodbLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://badmkavinda:{password}@sensezcluster.esoo75g.mongodb.net/?retryWrites=true&w=majority&appName=SensezCluster"

client = MongoClient(connection_string)
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