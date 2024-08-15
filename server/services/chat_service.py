from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from server.utils.logger import logger

# Initialize the model
model = ChatOpenAI(model="gpt-3.5-turbo")

# Define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

with_message_history = RunnableWithMessageHistory(prompt | model, get_session_history, input_messages_key="messages")

async def handle_chat(session_id: str, user_message: str) -> str:
    try:
        response = with_message_history.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config={"configurable": {"session_id": session_id}},
        )
        return response.content
    except Exception as e:
        logger.error(f"Error in handle_chat: {e}")
        raise e
