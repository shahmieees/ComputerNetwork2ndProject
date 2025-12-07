import socket
import threading
import random
import queue
import time

HOST = "10.121.178.56" # "192.168.0.149"
PORT = 12345

MIN_PLAYERS = 3
MAX_PLAYERS = 6
ROUNDS = 3

KEYWORDS = [
    "apple", "cat", "school", "mountain", "coffee",
    "keyboard", "moon", "river", "book", "car"
]

lock = threading.Lock()
start_signal = False  # NEW: global start trigger


class Player:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.name = None
        self.score = 0
        self.is_alien = False
        self.alive = True


players = []                 # Player objects
msg_queue = queue.Queue()    # (player_name, raw_message)


def send(conn, text):
    try:
        conn.sendall((text + "\n").encode())
    except:
        pass


def broadcast(text):
    with lock:
        for p in players:
            send(p.conn, text)


def client_listener(player: Player):
    global start_signal
    conn = player.conn

    try:
        buf = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode().strip()

                # START trigger
                if text.upper() == "START":
                    global start_signal
                    with lock:
                        #if len(players) >= MIN_PLAYERS:
                        start_signal = True
                        print(f"[INFO] {player.name} requested START.")
                        #broadcast(f"INFO|{player.name} requested to start the game.")
                        #else:
                            #send(conn, "INFO|Not enough players to start (min 3).")

                # All other messages go to queue
                else:
                    msg_queue.put((player.name, text))

    except:
        pass

    finally:
        player.alive = False
        with lock:
            if player in players:
                players.remove(player)
        print(f"[INFO] {player.addr} disconnected.")


def handle_new_connections(server_sock):
    print(f"[INFO] Server listening on {HOST}:{PORT}")
    server_sock.listen()

    while True:
        conn, addr = server_sock.accept()
        p = Player(conn, addr)
        threading.Thread(target=lambda: initial_handshake(p), daemon=True).start()


def initial_handshake(player: Player):
    global start_signal

    conn = player.conn
    try:
        data = conn.recv(4096).decode().strip()
        if not data:
            conn.close()
            return

        if data.startswith("JOIN|"):
            name = data.split("|", 1)[1].strip()
            player.name = name

            with lock:
                if len(players) >= MAX_PLAYERS:
                    send(conn, "ERROR|Room full")
                    conn.close()
                    return

                players.append(player)
                current = len(players)

            send(conn, f"INFO|Welcome {name}. Currently {current}/{MAX_PLAYERS} players.")
            print(f"[INFO] Player joined: {name} from {player.addr}")

            # Auto-start if room fills to max
            if current == MAX_PLAYERS:
                start_signal = True
                broadcast("INFO|Maximum number of players reached. Game starting now!")

            threading.Thread(target=client_listener, args=(player,), daemon=True).start()

        else:
            send(conn, "ERROR|Please send JOIN|username")
            conn.close()

    except:
        conn.close()


def wait_for_game_start():
    """Wait only for START or MAX_PLAYERS. MIN_PLAYERS is NOT auto-start."""
    global start_signal

    # reset the flag every time we enter the lobby
    start_signal = False

    print("[INFO] Waiting for START command or full room...")
    broadcast("INFO|Waiting for START command to begin the game "
              f"(requires at least {MIN_PLAYERS} players).")

    while True:
        with lock:
            count = len(players)
            full_room = (count == MAX_PLAYERS)
            local_start = start_signal

        # Case 1: room is full and enough players
        if full_room and count >= MIN_PLAYERS:
            print(f"[INFO] Room full ({count} players). Starting game automatically.")
            return

        # Case 2: someone pressed START
        if local_start:
            if count >= MIN_PLAYERS:
                print(f"[INFO] START accepted with {count} players. Starting game.")
                return
            else:
                # not enough players yet → reject and reset flag
                broadcast(f"INFO|Not enough players to start (need at least {MIN_PLAYERS}, "
                          f"currently {count}).")
                with lock:
                    start_signal = False   # reset and keep waiting

        time.sleep(0.3)


def collect_clues(keyword):
    pending = {}
    with lock:
        current_players = list(players)

    for p in current_players:
        pending[p.name] = None
        send(p.conn, "CLUE_REQ|Please enter your clue.")

    while True:
        try:
            pname, text = msg_queue.get(timeout=0.1)
        except queue.Empty:
            with lock:
                for p in current_players:
                    if not p.alive and p.name in pending:
                        pending.pop(p.name)
            if not pending:
                break
            continue

        if text.startswith("CLUE|"):
            _, sender, clue = text.split("|", 2)
            sender = sender.strip()
            if sender in pending and pending[sender] is None:
                pending[sender] = clue.strip()

        if all(v is not None for v in pending.values()):
            break

    result = []
    with lock:
        for p in current_players:
            if p.name in pending:
                result.append((p.name, pending[p.name]))
    return result


def collect_votes(alien_name):
    votes = {}
    with lock:
        current_players = list(players)

    for p in current_players:
        if not p.is_alien:
            send(p.conn, "VOTE_REQ|Send VOTE|name")

    needed = {p.name for p in current_players if not p.is_alien}

    while needed:
        try:
            pname, text = msg_queue.get(timeout=0.1)
        except queue.Empty:
            with lock:
                for p in current_players:
                    if not p.alive and p.name in needed:
                        needed.remove(p.name)
            continue

        if text.startswith("VOTE|"):
            target = text.split("|", 1)[1].strip()
            if pname in needed:
                votes[pname] = target
                needed.remove(pname)

    return votes


def collect_choices():
    choices = {}
    with lock:
        current_players = list(players)

    needed = {p.name for p in current_players}

    for p in current_players:
        send(p.conn, "CHOICE_REQ|NEXT or QUIT?")

    while needed:
        try:
            pname, text = msg_queue.get(timeout=0.1)
        except queue.Empty:
            with lock:
                for p in current_players:
                    if not p.alive and p.name in needed:
                        needed.remove(p.name)
            continue

        if text.startswith("CHOICE|"):
            choice = text.split("|")[1].strip().upper()
            if choice in ("NEXT", "QUIT") and pname in needed:
                choices[pname] = choice
                needed.remove(pname)

    return all(c == "NEXT" for c in choices.values())


def game_loop():
    while True:
        wait_for_game_start()

        with lock:
            if len(players) < MIN_PLAYERS:
                broadcast("INFO|Not enough players after waiting. Restarting lobby...")
                continue
            current_players = list(players)

        alien = random.choice(current_players)
        keyword = random.choice(KEYWORDS)

        for p in current_players:
            if p is alien:
                p.is_alien = True
                send(p.conn, "ROLE|ALIEN")
            else:
                p.is_alien = False
                send(p.conn, f"ROLE|HUMAN|{keyword}")

        broadcast("INFO|Game started! 3 rounds of clues ahead.")

        for r in range(1, ROUNDS + 1):
            broadcast(f"ROUND|{r}")
            clues = collect_clues(keyword)
            for nm, clue in clues:
                broadcast(f"BCLUE|{nm}|{clue}")
            broadcast("ROUND_END|Done with clues.")

        broadcast("PHASE|VOTING")
        votes = collect_votes(alien.name)

        correct = [v for v, t in votes.items() if t == alien.name]
        incorrect = len(votes) - len(correct)

        for p in current_players:
            if p.name in correct:
                p.score += 1
        alien.score += incorrect

        if correct:
            broadcast(f"RESULT|Correct voters: {','.join(correct)}")
        else:
            broadcast("RESULT|No correct guesses.")

        with lock:
            scores = "SCORE|" + "|".join(f"{p.name}:{p.score}" for p in current_players)
        broadcast(scores)

        if not collect_choices():
            broadcast("GAMEOVER|Players chose to quit. Closing room.")
            with lock:
                for p in players:
                    try:
                        send(p.conn, "BYE|Server shutting down.")
                        p.conn.close()
                    except:
                        pass
                players.clear()
            break

        broadcast("INFO|Starting new game shortly...")
        time.sleep(1)


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))

    threading.Thread(target=handle_new_connections, args=(srv,), daemon=True).start()

    try:
        game_loop()
    except KeyboardInterrupt:
        print("[INFO] Server shutting down.")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
