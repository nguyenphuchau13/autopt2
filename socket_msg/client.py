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
        self.send_message('', 'login')

    def send_message(self, msg, send_to):
        msg_meta_data = {
            self.client_name: {
                "msg_send": [
                    {
                        "send_to": send_to,
                        "msg": msg
                    }
                ]
            }
        }
        msg_data = json.dumps(msg_meta_data)
        msg_data += '*'
        self.client.send(msg_data.encode(self.FORMAT))

    def recv_msg(self):
        msg = self.client.recv(self.SIZE).decode(self.FORMAT)
        print(f"[SERVER] {msg}")
        return msg
