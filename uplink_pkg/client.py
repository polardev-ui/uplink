import os
import getpass
from prompt_toolkit import prompt
import requests

# Firebase config placeholder (replace with your actual config)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCR7zgL1QbgfLVeyoEJvWsB7ITGivka-Yg",
    "authDomain": "uplink-c269e.firebaseapp.com",
    "databaseURL": "https://uplink-c269e-default-rtdb.firebaseio.com",
    "storageBucket": "uplink-c269e.firebasestorage.app"
}

API_KEY = FIREBASE_CONFIG["apiKey"]
DATABASE_URL = FIREBASE_CONFIG["databaseURL"].rstrip("/")


def _firebase_auth(endpoint, payload):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={API_KEY}"
    response = requests.post(url, json=payload, timeout=20)
    data = response.json()
    if not response.ok:
        raise RuntimeError(data.get("error", {}).get("message", "Authentication failed"))
    return data


def _get_messages(id_token=None):
    params = {"auth": id_token} if id_token else None
    response = requests.get(f"{DATABASE_URL}/messages.json", params=params, timeout=20)
    data = response.json()
    if not response.ok:
        raise RuntimeError(data.get("error", "Unable to fetch messages"))
    return data or {}


def _push_message(message, id_token=None):
    params = {"auth": id_token} if id_token else None
    response = requests.post(f"{DATABASE_URL}/messages.json", params=params, json=message, timeout=20)
    data = response.json()
    if not response.ok:
        raise RuntimeError(data.get("error", "Unable to send message"))
    return data

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def main():
    clear()
    print("Welcome to Uplink! Type 'login' or 'register':")
    username = None
    id_token = None
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
                user = _firebase_auth(
                    "signUp",
                    {
                        "email": f"{username}@uplink.app",
                        "password": password,
                        "returnSecureToken": True,
                    },
                )
                id_token = user.get("idToken")
                print('Registration successful!')
                break
            except Exception as e:
                print('Registration failed:', e)
        elif action == 'login':
            username = prompt('Username: ')
            password = getpass.getpass('Password: ')
            try:
                user = _firebase_auth(
                    "signInWithPassword",
                    {
                        "email": f"{username}@uplink.app",
                        "password": password,
                        "returnSecureToken": True,
                    },
                )
                id_token = user.get("idToken")
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
        messages = _get_messages(id_token=id_token) or {}
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
        _push_message(f"{username}: {text}", id_token=id_token)
