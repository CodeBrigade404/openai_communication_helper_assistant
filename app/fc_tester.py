import time
from app.openai_client import client,assistant_id
from app import app
from app.mongodb_client import get_user_info

thread = client.beta.threads.create()
# Send message to OpenAI
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hey Mister, can you tell me detail of you like your name"
)

# Create and poll the run
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
    instructions="Please address the user politely and friendly give short answers 20 to 30 words"
)

# print(run.model_dump_json(indent=4))

while True:
    time.sleep(5)

    run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
    
    if run_status.status == "completed":
        message = client.beta.threads.messages.list(thread_id=thread.id)
    
        for msg in message.data:
            role = msg.role
            content = msg.content[0].text.value
            print(f"{role.capitalize()} : {content}")
        break
    elif run_status.status == "requires_action":
        required_actions = run_status.required_action.submit_tool_outputs.model_dump()
        tools_output =[]
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
                print("function not found")
        
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tools_output
        )

    else:
        print("Waiting ")
        time.sleep(5)   
