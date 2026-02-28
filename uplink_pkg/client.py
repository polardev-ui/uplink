import os
import getpass
from prompt_toolkit import prompt
import pyrebase

# Firebase config placeholder (replace with your actual config)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCR7zgL1QbgfLVeyoEJvWsB7ITGivka-Yg",
    "authDomain": "uplink-c269e.firebaseapp.com",
    "databaseURL": "https://uplink-c269e-default-rtdb.firebaseio.com",
    "storageBucket": "uplink-c269e.firebasestorage.app"
}

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def main():
    clear()
    print("Welcome to Uplink! Type 'login' or 'register':")
    while True:
        action = prompt('> ').strip().lower()
        if action == 'register':
            username = prompt('Username: ')
            password = getpass.getpass('Password: ')
            confirm = getpass.getpass('Confirm: ')
            if password != confirm:
                print('Passwords do not match.')
                continue
            try:
                user = auth.create_user_with_email_and_password(f"{username}@uplink.app", password)
                print('Registration successful!')
                break
            except Exception as e:
                print('Registration failed:', e)
        elif action == 'login':
            username = prompt('Username: ')
            password = getpass.getpass('Password: ')
            try:
                user = auth.sign_in_with_email_and_password(f"{username}@uplink.app", password)
                print('Login successful!')
                break
            except Exception as e:
                print('Login failed:', e)
        else:
            print("Type 'login' or 'register':")
    print('You are now in the public chat! (Type /quit to exit)')
    # Simple polling chat loop
    last_seen = 0
    while True:
        messages = db.child('messages').get().val() or {}
        # Firebase returns a dict of {key: message}, so convert to list
        if isinstance(messages, dict):
            # Sort by key to preserve order (Firebase keys are time-based)
            msg_list = [messages[k] for k in sorted(messages.keys())]
        elif isinstance(messages, list):
            msg_list = messages
        else:
            msg_list = []
        # Only print new messages since last_seen
        new_msgs = msg_list[-10:]
        clear()
        for m in new_msgs:
            print(m)
        text = prompt('> ')
        if text.strip() == '/quit':
            print('Goodbye!')
            break
        db.child('messages').push(f"{username}: {text}")
