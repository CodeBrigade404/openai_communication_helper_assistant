import os

os.environ["OPENAI_API_KEY"]

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")
response = llm.invoke("Hi")

print(response)


