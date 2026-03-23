import os
import getpass
import threading
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
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


def _normalize_messages(raw_messages):
    if isinstance(raw_messages, dict):
        items = sorted(raw_messages.items(), key=lambda item: item[0])
        return [(key, str(value)) for key, value in items]

    if isinstance(raw_messages, list):
        normalized = []
        for index, value in enumerate(raw_messages):
            if value is not None:
                normalized.append((str(index), str(value)))
        return normalized

    return []


def _fetch_new_messages(id_token, last_seen_key, first_load=False, first_load_limit=20):
    raw_messages = _get_messages(id_token=id_token) or {}
    messages = _normalize_messages(raw_messages)

    if not messages:
        return [], last_seen_key

    keys = [key for key, _ in messages]
    newest_key = keys[-1]

    if last_seen_key is None:
        if first_load:
            return [message for _, message in messages[-first_load_limit:]], newest_key
        return [], newest_key

    if last_seen_key in keys:
        last_index = keys.index(last_seen_key)
        new_messages = [message for _, message in messages[last_index + 1:]]
        return new_messages, newest_key

    return [message for _, message in messages[-first_load_limit:]], newest_key


def _print_help():
    print("Available commands:")
    print("  /help      Show this help menu")
    print("  /refresh   Show the latest messages now")
    print("  /clear     Clear the screen")
    print("  /quit      Exit Uplink")


def _handle_command(command_text, id_token):
    command = command_text.strip().lower()

    if command in {'/help', '/commands'}:
        _print_help()
        return False

    if command == '/clear':
        clear()
        return False

    if command == '/refresh':
        latest_messages, _ = _fetch_new_messages(id_token=id_token, last_seen_key=None, first_load=True)
        if not latest_messages:
            print('[system] No messages yet.')
            return False
        print('[system] Latest messages:')
        for message in latest_messages:
            print(message)
        return False

    if command == '/quit':
        print('Goodbye!')
        return True

    print("Unknown command. Type /help for available commands.")
    return False

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
    print('You are now in the public chat! Type /help for commands.')

    stop_event = threading.Event()
    session = PromptSession()
    last_seen_key = {'value': None}

    def poll_messages():
        first_load = True
        while not stop_event.is_set():
            try:
                new_messages, latest_key = _fetch_new_messages(
                    id_token=id_token,
                    last_seen_key=last_seen_key['value'],
                    first_load=first_load,
                )
                if latest_key is not None:
                    last_seen_key['value'] = latest_key
                for message in new_messages:
                    print(message)
                first_load = False
            except Exception as error:
                print(f"[system] Message sync error: {error}")

            stop_event.wait(1.0)

    poll_thread = threading.Thread(target=poll_messages, daemon=True)
    poll_thread.start()

    try:
        with patch_stdout(raw=True):
            while not stop_event.is_set():
                try:
                    text = session.prompt('> ', erase_when_done=True).strip()
                except (EOFError, KeyboardInterrupt):
                    text = '/quit'

                if not text:
                    continue

                if text.startswith('/'):
                    should_quit = _handle_command(text, id_token=id_token)
                    if should_quit:
                        break
                    continue

                _push_message(f"{username}: {text}", id_token=id_token)
    finally:
        stop_event.set()
        poll_thread.join(timeout=2)
