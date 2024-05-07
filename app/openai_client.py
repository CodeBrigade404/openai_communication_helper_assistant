# app/openai_client.py
import os
import time
import openai
from dotenv import load_dotenv
from app import app
from app.mongodb_client import get_user_info

load_dotenv()

api_key = os.getenv("OPEN_API_KEY")
client = openai.OpenAI(api_key=api_key)

assistant_id = os.getenv("ASSISTANT_ID")

def conversation_builder(thread_id, client, assistant_id , content):
    messages_list = []  # List to store messages

    # Send message to initiate conversation
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

    # Create and poll the run
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="""Please address the user politely and friendly and give short answers. 
        10 to 25 words; you are not an AI assistant; you are a hearing impaired person."""
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

        if run_status.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id)

            for msg in messages.data:
                message_info = {
                    'id': msg.id,
                    'assistant_id': msg.assistant_id,
                    'attachments': msg.attachments,
                    'completed_at': msg.completed_at,
                    'content': [content_block.to_dict() for content_block in msg.content],
                    'created_at': msg.created_at,
                    'incomplete_at': msg.incomplete_at,
                    'incomplete_details': msg.incomplete_details,
                    'metadata': msg.metadata,
                    'object': msg.object,
                    'role': msg.role,
                    'run_id': msg.run_id,
                    'status': msg.status,
                    'thread_id': msg.thread_id
                }
                messages_list.append(message_info)

            # Exit the loop after collecting messages
            break

        elif run_status.status == "requires_action":
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            tools_output = []
            for action in required_actions["tool_calls"]:
                func_name = action["function"]["name"]
                if func_name == "get_my_info":
                    output = get_user_info("MK")  
                    tools_output.append(
                        {
                            "tool_call_id": action["id"],
                            "output": output
                        }
                    )
                else:
                    print("Function not found")

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tools_output
            )

        else:
            print("Waiting ")

    return messages_list  # Return the list of messages


# messages_array = conversation_builder("thread_OlLKLaqmozIuh40gUjl9wFJ9", client, assistant_id ,"Hey Mister , can i know your birth date?")
# print(messages_array)
