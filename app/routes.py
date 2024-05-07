import hashlib
from flask import request, jsonify
from flask_jwt_extended import  create_access_token, jwt_required, get_jwt_identity
from app import app
from app.openai_client import client, assistant_id
from app.mongodb_client import users_collection
from app.functions import generate_user_paragraph
from dataclasses import asdict
from json import JSONDecodeError

# User registration
@app.route('/sign_up', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        else:
            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            new_user = {'username': username, 'password': hashed_password}
            users_collection.insert_one(new_user)
            return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Username and password are required'}), 400

# User login
@app.route('/sign_in', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = users_collection.find_one({'username': username})
        if user:
            # Check hashed password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user['password'] == hashed_password:
                # Generate JWT token
                access_token = create_access_token(identity=username)
                return jsonify(access_token=access_token), 200
            else:
                return jsonify({'error': 'Invalid password'}), 401
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Username and password are required'}), 400

# save user object
@app.route('/save_user', methods=['POST'])
@jwt_required()
def save_user():
    try:
        data = request.json
    except JSONDecodeError as e:
        return jsonify({'error': 'Failed to decode JSON object: ' + str(e)}), 400

    # Retrieve username from JWT identity
    username = get_jwt_identity() 
    if not username:
        return jsonify({'error': 'Failed to retrieve user identity from JWT'}), 400
    
    # Check if all required fields are present
    required_fields = ['f_name', 'l_name', 'gender', 'address', 'birth_date', 'about_me']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if gender is one of the specified types
    valid_genders = ['Male', 'Female', 'Other']
    if data['gender'] not in valid_genders:
        return jsonify({'error': 'Invalid gender type'}), 400
    
    # Process other_names if present
    other_names = data.get('other_names', [])

    # Save or process the user information
    user_info = {
        'f_name': data['f_name'],
        'l_name': data['l_name'],
        'other_names': other_names,
        'gender': data['gender'],
        'address': data['address'],
        'birth_date': data['birth_date'],
        'about_me': data['about_me']
    }

    # If function_call_string is not in the user_info object, add it
    if 'function_call_string' not in user_info:
        user_info['function_call_string'] = generate_user_paragraph(user_info)
    
    # Update user details in the user collection
    try:
        users_collection.update_one({'username': username}, {'$set': {'user_info': user_info}}, upsert=True)
    except Exception as e:
        return jsonify({'error': 'Failed to save user details: ' + str(e)}), 500

    return jsonify({'message': 'User details saved successfully'}), 201

# chat thread creating
@app.route('/create_thread', methods=['POST'])
@jwt_required() 
def create_thread():
    thread = client.beta.threads.create()
    thread_id = thread.id
    username = get_jwt_identity()  # Get the username from the JWT token

    # Update the thread_ids array for the user
    users_collection.update_one({'username': username}, {'$push': {'thread_ids': thread_id}})
    
    return jsonify({'thread_id': thread_id})

# chat 
@app.route('/ask', methods=['POST'])
@jwt_required()
def ask():
    content = request.json.get('content')
    thread_id = request.json.get('thread_id')

    if not thread_id:
        return jsonify({'error': 'thread_id is required'}), 400

    # Send message to OpenAI
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

 # Create and poll the run
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user politely and friendly give short answers 20 to 30 words"
    )

    retrieve_run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run.id
    )
    
    print(retrieve_run.model_dump_json(indent=2))
    
    return jsonify({'messages': "run"})
    # Create and poll the run
    # run = client.beta.threads.runs.create_and_poll(
    #     thread_id=thread_id,
    #     assistant_id=assistant_id,
    #     instructions="Please address the user politely and friendly give short answers 20 to 30 words"
    # )

    # if run.status == 'completed':
    #     # Get messages from OpenAI
    #     messages = client.beta.threads.messages.list(
    #         thread_id=thread_id
    #     )

    #     response_messages = []
    #     for msg in messages.data:
    #         message_dict = {
    #             'id': msg.id,
    #             'assistant_id': msg.assistant_id,
    #             'attachments': msg.attachments,
    #             'completed_at': msg.completed_at,
    #             'content': [content_block.to_dict() for content_block in msg.content],
    #             'created_at': msg.created_at,
    #             'incomplete_at': msg.incomplete_at,
    #             'incomplete_details': msg.incomplete_details,
    #             'metadata': msg.metadata,
    #             'object': msg.object,
    #             'role': msg.role,
    #             'run_id': msg.run_id,
    #             'status': msg.status,
    #             'thread_id': msg.thread_id
    #         }
    #         response_messages.append(message_dict)

    # return jsonify({'messages': run})
    # else:
    #     return jsonify({'error': 'Run not completed'}), 500
