import socket
import json
import threading


class SocketClient:
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    ADDR = (HOST, PORT)
    IP = socket.gethostbyname(socket.gethostname())
    SIZE = 1024
    FORMAT = "utf-8"
    DISCONNECT_MSG = "!DISCONNECT"

    def __init__(self, client_name):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.client_name = client_name

    def send_message(self, msg):
        msg_meta_data = {
            self.client_name: {
                "msg_send": [
                    {
                        "send_to": "slave",
                        "msg": msg
                    }
                ]
            }
        }
        msg_data = json.dumps(msg_meta_data)
        self.client.send(msg_data.encode(self.FORMAT))

    def recv_msg(self, client_socket):
        msg = client_socket.recv(self.SIZE).decode(self.FORMAT)
        print(f"[SERVER] {msg}")
        return msg
