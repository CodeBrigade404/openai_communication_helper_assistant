from langchain_community.document_loaders.mongodb import MongodbLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from server.utils.mongodb_client import connection_string

loader = MongodbLoader(
    connection_string=connection_string,
    db_name="sensez",
    collection_name="senceez_user_collection",
    filter_criteria={"username": "Dilshan"},
)

docs = loader.load()

len(docs)

print(docs[0])

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 50)
docss = text_splitter.split_documents(docs)

print(docss)
