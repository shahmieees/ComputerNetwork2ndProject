# ComputerNetwork2ndProject

🎮 Multiplayer Social Deduction Game (TCP Client–Server)

A custom-built multiplayer social deduction game implemented using Python TCP sockets.
This project was created as part of Computer Networks – Project 4: Build Your Own Service.

The game supports 3–6 players and allows them to join a lobby, receive hidden roles, give clues, vote, and score points—all coordinated by a central server using a custom communication protocol.

🚀 Features
🖥 Centralized Game Server (gameserver.py)

Accepts multiple TCP client connections

Registers usernames and tracks player states

Randomly assigns roles (1 Alien + Humans with keyword)

Coordinates:

3 rounds of clue submissions

Voting

Scoring and round results

Maintains persistent scoreboard across games

Controls game flow using a custom protocol

Starts the game only when:

A player types START and at least 3 players are connected

The room reaches maximum capacity (6 players) → auto-start

Prevents auto-start when exactly 3 players join (old behavior removed)

🎮 Client Application (gameclient.py)

Connects to the server and sends JOIN|username

Receives role assignment and round instructions

Sends clue messages and votes

Types START to begin the game (requires ≥3 players)

Types QUIT to exit the session

Displays server broadcasts in real time

Uses threading to receive messages in background while allowing player input

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
