import socket
import json
import threading
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

ADDR = (HOST, PORT)
IP = socket.gethostbyname(socket.gethostname())
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    connected = True
    client_name = 'bill gates'

    while connected:
        msg = input(">input: ")
        msg_meta_data = {
            'bill gates': {
                "msg_send": [
                    {
                        "send_to": "slave",
                        "msg": msg
                    }
                ]
            }
        }
        msg_data = json.dumps(msg_meta_data)
        client.send(msg_data.encode(FORMAT))

        if msg == DISCONNECT_MSG:
            connected = False
        else:
            thread = threading.Thread(target=recv_msg, args=(client,))
            thread.start()
def recv_msg(client_socket):
    msg = client_socket.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")

if __name__ == "__main__":
    main()