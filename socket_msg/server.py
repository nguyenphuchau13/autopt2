import socket
import threading
import json

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

ADDR = (HOST, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"


def handle_client(conn, addr, client_info):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        msg_data = json.loads(msg)
        client_name = list(msg_data.keys())[0]
        print(msg_data)
        print(client_name)
        if client_name not in client_info.keys():
            client_info[client_name] = {'conn': conn}
        else:
            client_info[client_name]['conn'] = conn

        if msg == DISCONNECT_MSG:
            connected = False

        print(f"[{addr}] {msg}")
        for idx in range(0, len(msg_data[client_name]['msg_send'])):
            msg_send = msg_data[client_name]['msg_send'].pop()
            send_to = msg_send['send_to']
            conn_send_to = client_info.get(send_to, None)
            if conn_send_to is None:
                print('client name {} not found'.format(send_to))
                client_info.setdefault(send_to, {}).setdefault('msg_rev', []).append(msg_send)
            else:
                conn_send_to['conn'].send(msg_send['msg'].encode(FORMAT))
        for idx in range(0, len(client_info[client_name].get('msg_rev', []))):
            msg_rev = client_info[client_name]['msg_rev'].pop()
            conn.send(msg_rev['msg'].encode(FORMAT))
    conn.close()

def main():
    print("[STARTING] Server is starting...")
    server = socket_msg.socket_msg(socket_msg.AF_INET, socket_msg.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    cline_name = 0
    client_info = {}
    while True:
        conn, addr = server.accept()
        print(conn, addr)
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_info))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()
