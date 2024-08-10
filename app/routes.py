import hashlib
import time
from flask import request, jsonify
from flask_jwt_extended import  create_access_token, jwt_required, get_jwt_identity
from app import app
from app.openai_client import client, assistant_id ,conversation_builder
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
    names = data.get('names', {})
    f_name = names.get('f_name')
    l_name = names.get('l_name')
    surname = names.get('surname')  # Optional
    nick_name = names.get('nick_name') # Optional
    birth_date = data.get('birth_date')
    address = data.get('address')
    mobile_number = data.get('mobile_number')
    guardian_mobile_number = data.get('guardian_mobile_number')  # Optional
    email = data.get('email')  # Optional
    about_me = data.get('about_me')  

    # Collect missing fields
    missing_fields = []
    if not username:
        missing_fields.append('Username')
    if not password:
        missing_fields.append('Password')
    if not f_name:
        missing_fields.append('First name')
    if not l_name:
        missing_fields.append('Last name')
    if not birth_date:
        missing_fields.append('Birth date')
    if not address:
        missing_fields.append('Address')
    if not mobile_number:
        missing_fields.append('Mobile number')
    if not about_me:
        missing_fields.append('About Me')

    if missing_fields:
        error_message = f"Please provide the following required fields: {', '.join(missing_fields)}."
        return jsonify({'error': error_message}), 400

    # Check for existing user
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'The username is already taken. Please choose a different username.'}), 400

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Create new user
    new_user = {
        'username': username,
        'password': hashed_password,
        'names': {
            'f_name': f_name,
            'l_name': l_name,
            'surname': surname,
            'nick_name': nick_name
        },
        'birth_date': birth_date,
        'address': address,
        'mobile_number': mobile_number,
        'guardian_mobile_number': guardian_mobile_number,  # Optional
        'email': email, # Optional
        'about_me': about_me
    }
    users_collection.insert_one(new_user)
    return jsonify({'message': 'Registration successful! Welcome to our platform.'}), 201


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
    # Create the thread
    thread = client.beta.threads.create()
    thread_id = thread.id
    username = get_jwt_identity()  

    # Update the thread_ids array for the user
    users_collection.update_one({'username': username}, {'$push': {'thread_ids': thread_id}})

    return jsonify({'thread_id': thread_id})




@app.route('/ask', methods=['POST'])
@jwt_required()
def ask():
    try:
        content = request.json.get('content')
        thread_id = request.json.get('thread_id')

        if not thread_id:
            return jsonify({'error': 'thread_id is required'}), 400
        
        username = get_jwt_identity()  

        # Call interact_with_user function to get the array of messages
        messages_array = conversation_builder(thread_id, client, assistant_id, content , username)

        # Return the array of messages as JSON response
        return jsonify(messages_array)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

