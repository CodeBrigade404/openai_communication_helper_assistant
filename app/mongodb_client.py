# app/mongodb_client.py
import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://badmkavinda:{password}@sensezcluster.esoo75g.mongodb.net/?retryWrites=true&w=majority&appName=SensezCluster"

client = MongoClient(connection_string)
db = client.sensez
users_collection = db.users

def get_user_info(username):
    user = users_collection.find_one({'username': username})
    if user:
        user_info = user.get('user_info')
        if user_info:
            # Return function_call_string if it exists, or an empty string otherwise
            return user_info.get('function_call_string', '')
    return ''  # Return an empty string if user or user_info doesn't exist

print(get_user_info("MK"))