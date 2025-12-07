import socket
import threading
import sys
import random

SERVER_HOST = "10.121.178.56" # "192.168.0.149"
SERVER_PORT = 12345

client_name = None
role = None
keyword = None


def send(sock, text):
    try:
        sock.sendall((text + "\n").encode())
    except:
        print("[ERROR] Failed to send.")
        sock.close()
        sys.exit(0)


def handle_server_message(msg, sock):
    global role, keyword

    if msg.startswith("INFO|"):
        print("[INFO]", msg.split("|", 1)[1])

    elif msg.startswith("ERROR|"):
        print("[ERROR]", msg.split("|", 1)[1])

    elif msg.startswith("ROLE|"):
        parts = msg.split("|")
        if parts[1] == "ALIEN":
            role = "ALIEN"
            print("[ROLE] You are the ALIEN. You don't know the keyword!")
        else:
            role = "HUMAN"
            keyword = parts[2]
            print(f"[ROLE] You are HUMAN. Keyword: '{keyword}'")

    elif msg.startswith("ROUND|"):
        print("\n--- ROUND", msg.split("|")[1], "---")

    elif msg.startswith("CLUE_REQ|"):
        print("[ACTION] Type one short clue sentence (no direct mention of keyword). *Press Enter first.")
        clue = input("Your clue: ").strip()
        if not clue:
            clue = "(no clue)"
        send(sock, f"CLUE|{client_name}|{clue}")

    elif msg.startswith("BCLUE|"):
        _, nm, clue = msg.split("|", 2)
        print(f"[CLUE] {nm}: {clue}")

    elif msg.startswith("ROUND_END|"):
        print("[INFO] Round finished.")

    elif msg.startswith("PHASE|VOTING"):
        print("\n[VOTING] Voting phase begins.")

    elif msg.startswith("VOTE_REQ|"):
        vote = input("[ACTION] Vote for: ").strip()
        send(sock, f"VOTE|{vote}")

    elif msg.startswith("RESULT|"):
        print("[RESULT]", msg.split("|")[1])

    elif msg.startswith("SCORE|"):
        scores = msg.split("|")[1:]
        print("\n[SCORES]")
        for line in scores:
            print(" -", line)

    elif msg.startswith("CHOICE_REQ|"):
        choice = ""
        while choice.upper() not in ("NEXT", "QUIT"):
            choice = input("[ACTION] NEXT or QUIT: ").strip().upper()
        send(sock, f"CHOICE|{choice}")

    elif msg.startswith("GAMEOVER|"):
        print("[GAMEOVER]", msg.split("|", 1)[1])
        sock.close()
        sys.exit(0)

    elif msg.startswith("BYE|"):
        print("[BYE]", msg.split("|", 1)[1])
        sock.close()
        sys.exit(0)

    else:
        print("[MSG]", msg)


def recv_loop(sock):
    buffer = b""
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("[INFO] Server closed connection.")
                break

            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                text = line.decode().strip()
                if text:
                    handle_server_message(text, sock)
    except:
        pass

    finally:
        sock.close()
        sys.exit(0)


def main():
    global client_name

    host = SERVER_HOST
    port = SERVER_PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print("[ERROR] Connection failed:", e)
        return

    client_name = input("Enter your username: ").strip()
    if not client_name:
        client_name = f"Player{random.randrange(1000)}"

    send(sock, f"JOIN|{client_name}")

    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()

    print("[INFO] Type START to begin the game (requires ≥3 players) and QUIT for exit.\n")

    while True:
        cmd = input("").strip()
        if cmd.lower() == "quit":
            send(sock, "CHOICE|QUIT")
            sock.close()
            break

        elif cmd.upper() == "START":
            send(sock, "START")

        else:
            pass  # no-op, client input not used outside prompts


if __name__ == "__main__":
    main()
