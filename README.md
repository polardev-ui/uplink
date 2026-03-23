# Uplink

Uplink is a terminal-based public chat room with authentication, powered by Firebase.

## Features

- Public chat room
- User registration and login (username, password)
- Real-time chat via Firebase

## Installation

### Option A: Install directly from GitHub

```bash
python3 -m pip install --upgrade pip
python3 -m pip install "git+https://github.com/polardev-ui/uplink.git"
```

Then run:

```bash
uplink
```

### Option B: Clone the repo (recommended for local development)

```bash
git clone https://github.com/polardev-ui/uplink.git
cd uplink
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Then run:

```bash
uplink
```

## Full setup checklist (after install)

1. Make sure you are on Python 3.8+:

```bash
python3 --version
```

1. If you cloned the repo, activate your virtual environment each new terminal session:

```bash
source .venv/bin/activate
```

1. Launch the app:

```bash
uplink
```

1. In-app, choose `register` (first time) or `login`.

2. Start chatting. Use `/quit` to exit.

## Running the server script (optional/local)

The packaged CLI client uses Firebase. A separate local websocket server script also exists for experimentation:

```bash
python3 uplink_server.py
```

This uses `users.json` locally and listens on port `8765`.

## Usage

```bash
uplink
```

Follow the prompts to register or log in, then chat in the public room.

### In-app commands

- `/help` - show available commands
- `/refresh` - print the latest messages immediately
- `/clear` - clear the terminal screen
- `/quit` - exit Uplink

## Requirements

- Python 3.8+
- See requirements.txt for dependencies

## Troubleshooting

- `uplink: command not found`: install with `python3 -m pip install -e .` (clone flow) or re-open terminal after install.
- Authentication errors: check internet access and try again.
- Dependency issues: run `python3 -m pip install --upgrade pip` and reinstall requirements.

---
This is a prototype. Do not use for sensitive data.
