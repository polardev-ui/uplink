import asyncio
import websockets
import bcrypt
import json

USERS_FILE = 'users.json'
PORT = 8765

connected = set()

# Load or initialize user database
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()

async def register_user(websocket):
    await websocket.send('Enter new username:')
    username = await websocket.recv()
    if username in users:
        await websocket.send('Username already exists.')
        return False
    await websocket.send('Enter password:')
    password = await websocket.recv()
    await websocket.send('Confirm password:')
    confirm = await websocket.recv()
    if password != confirm:
        await websocket.send('Passwords do not match.')
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed
    save_users(users)
    await websocket.send('Registration successful!')
    return username

async def login_user(websocket):
    await websocket.send('Enter username:')
    username = await websocket.recv()
    if username not in users:
        await websocket.send('Username not found.')
        return False
    await websocket.send('Enter password:')
    password = await websocket.recv()
    if bcrypt.checkpw(password.encode(), users[username].encode()):
        await websocket.send('Login successful!')
        return username
    else:
        await websocket.send('Incorrect password.')
        return False

async def handler(websocket):
    connected.add(websocket)
    try:
        await websocket.send('Welcome to Uplink! Type "login" or "register":')
        authed = False
        username = None
        while not authed:
            cmd = await websocket.recv()
            if cmd == 'register':
                username = await register_user(websocket)
                authed = bool(username)
            elif cmd == 'login':
                username = await login_user(websocket)
                authed = bool(username)
            else:
                await websocket.send('Type "login" or "register":')
        await websocket.send(f'You are now in the public chat, {username}!')
        async for message in websocket:
            for conn in connected:
                if conn != websocket:
                    await conn.send(f'{username}: {message}')
    finally:
        connected.remove(websocket)

async def main():
    async with websockets.serve(handler, '', PORT):
        print(f'Uplink server running on port {PORT}')
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
