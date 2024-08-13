import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.document_loaders import DirectoryLoader
from langchain.llms import openai
from langchain.chains import retrieval_qa
from dotenv import load_dotenv
from app.mongodb_client import sample_user_collection

load_dotenv()

openai_key = os.environ.get("OPEN_API_KEY")

loader = DirectoryLoader('./data', glob="./*.txt" ,show_progress=True)
data = loader.load()

embeddings = OpenAIEmbeddings(openai_api_key=openai_key)

vector_store = MongoDBAtlasVectorSearch.from_documents(data,embeddings,collection=sample_user_collection)




