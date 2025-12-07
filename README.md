# ComputerNetwork2ndProject

🎮 Multiplayer Social Deduction Game (TCP Client–Server)

A custom-built multiplayer social deduction game implemented using Python TCP sockets.
This project was created as part of Computer Networks – Project 4: Build Your Own Service.

The game supports 3–6 players and allows them to join a lobby, receive hidden roles, give clues, vote, and score points—all coordinated by a central server using a custom communication protocol.

🚀 Features

Centralized Game Server
1. Accepts JOIN requests from multiple clients
2. Tracks player names, roles, scores, and connection status
3. Assigns hidden roles (1 Alien + remaining Humans)
4. Selects a random secret keyword for Humans
5. Manages 3 clue rounds, voting phase, and scoring
6. 6. Broadcasts all game updates to connected clients

Client Application
1. Connects to server and submits username
2. Displays all broadcast messages (roles, clues, round prompts, results, scores)
3. Allows players to input clues and cast votes
4. Supports sending the START command to begin the game
5. Provides an interactive, text-based interface in the terminal

🏁 Game Start Rules

The game begins when:

A player types START, and

At least 3 players are connected

The player count reaches 6 (MAX_PLAYERS)

Server automatically starts the game

If a player types START while fewer than 3 players are connected, the server responds:

INFO|Not enough players to start (min 3).

🧩 Game Flow

Players join using JOIN|username

START or auto-start triggers role assignment:

ALIEN → does not know the keyword

HUMAN → keyword is revealed

Three rounds begin:

Each player submits one clue

All clues are broadcast to everyone

Voting phase to identify the Alien

Scoring:

Humans earn points for correct guesses

Alien earns points when Humans guess incorrectly

Players choose:

NEXT → continue with a new keyword

QUIT → exit the session

📁 Project Structure
├── gameserver.py     # Main game server (TCP)
├── gameclient.py     # Client application
└── README.md

🛠 Installation & Usage
1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

2. Start the game server
python gameserver.py


The server will display:

[INFO] Server listening on <IP>:12345
[INFO] Waiting for START command or full room...

3. Start clients (3–6 players)

Open multiple terminals:

python gameclient.py


Enter username when prompted.

4. Start the game

Any client may type:

START


(Requires ≥3 players)
