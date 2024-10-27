import json
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
from server.utils.mongodb_client import connection_string, get_user_details,custom_mongodb_loader
from server.utils.logger import logger

# Initialize the llm
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 50)

# Contextualize question
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question,"
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
# system_prompt = (
#     "You are an hearing-impaired person"
#     "Your personal details are provided"
#     "Use only the following pieces of retrieved context to answer the question. "
#     "If you don't know the answer based on the context, say 'The information is not available in the details provided.' "
#     "Do not use any outside knowledge or make assumptions. "
#     "Use three sentences maximum and keep the answer concise."
#     "\n\n"
#     "{context}"
# )
# system_prompt = (
#     "You are a hearing-impaired person. "
#     "Your personal details are provided. "
#     "If you don't know the answer based on the context, just return empty list [] "
#     "Provide 4 answers as a Python list. Each string in the list should be a variation of the answer. "
#     "The first should be a short one-word answer. "
#     "The second should be a normal response. "
#     "The third should be a bit longer. "
#     "The fourth should be the longest, using up to four sentences. "
#     "Return the answers directly as a list in this format: [\"answer1\", \"answer2\", \"answer3\", \"answer4\"]."
#     "\n\n"
#     "{context}"
# )

system_prompt = (
    "You are a hearing-impaired person."
    "Your personal details are provided. "
    "If you don't know the answer, just return empty list []"
    "Provide 4 answers as a Python list. Each string in the list should be a variation of the answer. "
    "The first should be a short one-word answer. "
    "The second should be a normal response. "
    "The third should be a bit longer. "
    "The fourth should be the longest, using up to four sentences. "
    "Return the answers directly as a list in this format: [\"answer1\", \"answer2\", \"answer3\", \"answer4\"]."
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


async def handle_chat(request: ChatRequest, token_data: dict) -> str:
    try:
        # Print the username for debugging
        logger.info(f"Processing request for user: {token_data['username']}")
        
        # Load documents from MongoDB
        user_docs = custom_mongodb_loader(
            connection_string,
            "sensez",
            "senceez_user_collection",
            {"username": token_data['username']}
        )
        
        if not user_docs:
            logger.error("No documents found for the given filter criteria.")
            return "No documents found."

        logger.info(f"Retrieved {len(user_docs)} documents.")
        logger.info(f"Documents {user_docs}")

        # Split the documents
        splits = text_splitter.split_documents(user_docs)
        if not splits:
            logger.error("No document splits generated from the retrieved documents.")
            return "No document splits available."

        logger.info(f"Generated {len(splits)} document splits.")

        # Initialize Chroma vector store
        try:
            vector_store = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
            retriever = vector_store.as_retriever()
        except Exception as e:
            logger.error(f"Error initializing Chroma vector store: {e}")
            return "Vector store initialization failed."

        # Create the history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # Create the RAG chain
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        # Initialize the conversational RAG chain
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

        # Invoke the conversational RAG chain
        ai_response = conversational_rag_chain.invoke(
            {"input": request.user_message},
            config={"configurable": {"session_id": request.session_id}},
        )

        logger.info(f"Generated AI response: {ai_response}")
        return ai_response

    except Exception as e:
        logger.error(f"Error in handle_chat: {e}")
        raise e