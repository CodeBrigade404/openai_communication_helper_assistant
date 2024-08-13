import hashlib
from flask import request, jsonify
from flask_jwt_extended import  create_access_token
from app import app
from app.mongodb_client import users_collection 
from dataclasses import asdict


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
