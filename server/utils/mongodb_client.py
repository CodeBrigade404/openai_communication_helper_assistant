# mongodb_client.py

import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_community.document_loaders.mongodb import MongodbLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

load_dotenv()

password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://badmkavinda:{password}@sensezcluster.esoo75g.mongodb.net/?retryWrites=true&w=majority&appName=SensezCluster"

client = MongoClient(connection_string)
db = client.sensez

# llm = ChatOpenAI(model="gpt-4o-mini")

# loader = MongodbLoader(
#     connection_string=connection_string,
#     db_name="sensez",
#     collection_name="senceez_user_collection",
#     filter_criteria={"username": "Dilshan"},
# )

# docs = loader.load()

# len(docs)

# text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 50)
# docss = text_splitter.split_documents(docs)

# vectorstore = Chroma.from_documents(documents=docss, embedding=OpenAIEmbeddings())

# retriever = vectorstore.as_retriever(search_type = "similarity", search_kwargs = {"k": 1})
# retrieved_docs = retriever.invoke("What is your name?")


# # 2. Incorporate the retriever into a question-answering chain.
# system_prompt = (
#     "You are an assistant for question-answering tasks. "
#     "Use the following pieces of retrieved context to answer "
#     "the question. If you don't know the answer, say that you "
#     "don't know. Use three sentences maximum and keep the "
#     "answer concise."
#     "\n\n"
#     "{context}"
# )

# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ]
# )

# question_answer_chain = create_stuff_documents_chain(llm, prompt)
# rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# response = rag_chain.invoke({"input": "What is your name?"})
# response["answer"]
# print(response["answer"])