
def generate_user_paragraph(user_info):
    paragraph = f"Name: {user_info['f_name']} {user_info['l_name']}\n"
    if user_info.get('other_names'):
        paragraph += f"Other Names: {', '.join(user_info['other_names'])}\n"
    paragraph += f"Gender: {user_info['gender']}\n"
    paragraph += f"Address: {user_info['address']}\n"
    paragraph += f"Birth Date: {user_info['birth_date']}\n"
    paragraph += f"About Me: {user_info['about_me']}\n"
    return paragraph