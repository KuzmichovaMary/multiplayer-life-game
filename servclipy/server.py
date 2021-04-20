import socket
from _thread import start_new_thread
import sys
import pickle
from life import Life


def read_data(data):
    data = data[1:-1].split()
    command = data[0]
    args = []
    for arg in data[1:]:
        if ":" not in arg:
            args.append(arg)
        else:
            d_type, value = arg.split(":")
            if d_type == "int":
                args.append(int(value))
            else:
                args.append(value)
    return command, args


MY_IPV4 = "192.168.1.150"
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5555
BUFF_SIZE = 4096


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.n_players = 0
        self.cells = {
            # player_id: {(), (), }
        }
        self.life = Life()

    def new_threaded_client(self, connection):
        data = self.make_color()
        connection.send(data.encode())
        while True:
            try:
                data = connection.recv(BUFF_SIZE).decode()
                print(f"Received: {data}")
                cmd, args = read_data(data)
                if cmd == "get_alive":
                    print("HERE")
                    print(pickle.dumps(self.life.alive))
                    connection.sendall(pickle.dumps(self.life.alive))
                elif cmd == "toggle":
                    x, y, color = args
                    self.life.toggle(x, y, color)
                if not data:
                    print("Disconnected.")
                    break

            except:
                break

        print("Lost connection.")
        connection.close()

    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as error:
            print(error)

        self.socket.listen(4)
        print(f"Server started at {self.host} {self.port}")

        while True:
            connection, address = self.socket.accept()
            print(f"Connection with {address} established.")

            self.n_players += 1
            start_new_thread(self.new_threaded_client, (connection,))

    def make_color(self):
        return f"(color int:{self.n_players})"


# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# try:
#     s.bind((HOST, PORT))
# except socket.error as e:
#     print(e)
#
# s.listen(2)
# print("Waiting for connection. Server started...")


def read_position(str):
    str = str.split(",")
    return int(str[0]), int(str[1])


pos = [(0, 0), (100, 100)]


# def threadedClient(conn, player):
#     conn.send(str.encode(make_color(pos[player])))
#     reply = ""
#     while True:
#         try:
#             data = read_position(conn.recv(2048).decode())
#             pos[player] = data
#
#             if not data:
#                 print("Disconnected...")
#                 break
#             else:
#                 if player == 1:
#                     reply = pos[0]
#                 else:
#                     reply = pos[1]
#                 print("Received :", data)
#                 print("Sending  :", reply)
#
#             conn.sendall(str.encode(make_color(reply)))
#         except:
#             break
#
#     print("Lost connection")
#     conn.close()
#
#
# currentPlayer = 0
# while True:
#     conn, addr = s.accept()
#     print("Connected to:", addr)
#
#     start_new_thread(threadedClient, (conn, currentPlayer))
#     currentPlayer += 1

server = Server()
server.start_server()
