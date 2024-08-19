from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders.mongodb import MongodbLoader
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from server.models.chat import ChatRequest
from server.utils.mongodb_client import connection_string, db
from server.utils.logger import logger

# Initialize the llm
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 50)

# Contextualize question
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


# Answer question 
system_prompt = (
    "You are an hearing-impaired person"
    "Your personal details are provided"
    "Use only the following pieces of retrieved context to answer the question. "
    "If you don't know the answer based on the context, say 'The information is not available in the details provided.' "
    "Do not use any outside knowledge or make assumptions. "
    "Use three sentences maximum and keep the answer concise."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)


async def handle_chat(request: ChatRequest ,token_data: dict ) -> str:
    try:
       
        loader =MongodbLoader(
            connection_string=connection_string,
            db_name="sensez",
            collection_name="senceez_user_collection",
            filter_criteria={"username": token_data["username"]},
        )
        
        user_docs = [doc async for doc in loader.alazy_load()]
    
        splits = text_splitter.split_documents(user_docs)

        vector_store = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
        retriever = vector_store.as_retriever()

        history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
        )

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            lambda session_id: MongoDBChatMessageHistory(
                session_id=session_id,
                connection_string=connection_string,
                database_name="sensez",
                collection_name="runtime_chat_memory_collection",
            ),
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        response = conversational_rag_chain.invoke(
            {"input": request.user_message},
            config={"configurable": {"session_id": request.session_id}},
        )
  
        return response
    except Exception as e:
        logger.error(f"Error in handle_chat: {e}")
        raise e
