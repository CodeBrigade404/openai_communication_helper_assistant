# app/routes.py
from app import app
from flask import request, jsonify
from app.openai_client import client

assistant_id = "asst_dVxwEioD2LZPmcXvHIsmaQ9a"
thread_id = "thread_ekFvL7J53LrD5F10e4i3Ryi4"

@app.route('/ask', methods=['POST'])
def ask():
    content = request.json.get('content')

    # Send message to OpenAI
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

    # Create and poll the run
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user politely and friendly"
    )

    if run.status == 'completed':
        # Get messages from OpenAI
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        response = messages.data[0].content[0].text.value
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'Run not completed'}), 500
