# app/routes.py
import os
from app import app
from flask import request, jsonify
from app.openai_client import client
from app.mongodb_client import users_collection
import hashlib
from dataclasses import asdict

assistant_id = os.getenv("ASSISTANT_ID")
thread_id = "thread_ekFvL7J53LrD5F10e4i3Ryi4"

@ app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email and password:
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        else:
            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            new_user = {'email': email, 'password': hashed_password}
            users_collection.insert_one(new_user)
            return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Email and password are required'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email and password:
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    else:
        return jsonify({'error': 'Email and password are required'}), 400
    


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

        response_messages = []
        for msg in messages.data:
            message_dict = {
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
            response_messages.append(message_dict)

        return jsonify({'messages': response_messages})
    else:
        return jsonify({'error': 'Run not completed'}), 500