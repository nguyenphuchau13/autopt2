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
        if msg == '':
            continue
        for msg_data in msg.split('*'):
            if msg_data == '':
                continue
            msg_data = json.loads(msg_data)
            client_name = list(msg_data.keys())[0]
            if client_name not in client_info.keys():
                client_info[client_name] = {'conn': conn}
            else:
                client_info[client_name]['conn'] = conn

            for idx in range(0, len(msg_data[client_name]['msg_send'])):
                msg_send = msg_data[client_name]['msg_send'].pop()

                send_to = msg_send['send_to']
                conn_send_to = client_info.get(send_to, None)

                if msg_send['msg'] == DISCONNECT_MSG:
                    client_info.pop(client_name)
                    connected = False

                    break
                if msg_send['msg'] == '':
                    print('ignore message init')
                    continue
                if conn_send_to is None or conn_send_to.get('conn', None) is None:
                    print('client name {} not found'.format(send_to))
                    client_info.setdefault(send_to, {}).setdefault('msg_rev', []).append(msg_send)

                else:
                    conn_send_to['conn'].send(msg_send['msg'].encode(FORMAT))
            if not connected:
                continue
            for idx in range(0, len(client_info[client_name].get('msg_rev', []))):
                msg_rev = client_info[client_name]['msg_rev'].pop()

                conn.send(msg_rev['msg'].encode(FORMAT))
    print('close connect ....')
    conn.close()

def send_message(client_info, client_name):
    connected = True
    while connected:
        client_data = client_info.get(client_name, None)
        if client_data:
            msg_sends = client_data.get('msg_send')
            if len(msg_sends) > 0:
                client_info = client_info.get(client_name, None)
    # conn.close()


def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    client_info = {}
    while True:

        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_info))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()
