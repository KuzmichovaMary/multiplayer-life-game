import socket
from _thread import start_new_thread
import sys
import pickle
from life import Life
from time import time
from config import COLORS


FIRST_PLAYER = 1


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


def seconds_to_minutes(time_in_seconds):
    return time_in_seconds / 60


def ms_to_seconds(time_in_milliseconds):
    return time_in_milliseconds / 1000


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
        self.round_time = 0.5
        self.eating_time = 0.1
        self.start_round_time = None
        self.start_eating_time = None
        self.show_info_time = 5 / 12  # minutes

    def new_threaded_client(self, connection):
        data = self.make_color()
        connection.sendall(data.encode())
        while True:
            try:
                data = connection.recv(BUFF_SIZE).decode()
                print(f"Received: {data}")
                cmd, args = read_data(data)
                if cmd == "get_alive":
                    connection.sendall(pickle.dumps(self.life.alive))
                elif cmd == "toggle":
                    x, y, color = args
                    self.life.toggle(x, y, color)
                elif cmd == "start_new_round?":
                    if args[0] == FIRST_PLAYER:
                        if seconds_to_minutes(time()) - self.start_eating_time > self.eating_time:
                            answer = b"(yes )"
                            self.start_round_time = seconds_to_minutes(time())
                            self.round_time += self.show_info_time
                            self.life = Life()
                        else:
                            answer = b"(no )"
                    else:
                        if seconds_to_minutes(time()) - self.start_eating_time > self.eating_time:
                            answer = b"(yes )"
                        else:
                            answer = b"(no )"
                    connection.sendall(answer)
                elif cmd == "start_eating?":
                    if args[0] == FIRST_PLAYER:
                        if seconds_to_minutes(time()) - self.start_round_time > self.round_time:
                            answer = b"(yes )"
                            self.start_eating_time = seconds_to_minutes(time())
                        else:
                            answer = b"(no )"
                    else:
                        if seconds_to_minutes(time()) - self.start_round_time > self.round_time:
                            answer = b"(yes )"
                        else:
                            answer = b"(no )"
                    connection.sendall(answer)
                elif cmd == "test_message":
                    connection.sendall(b"-------------------------------- Hello client -----------------------------------")
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

            if self.n_players == 0:
                self.start_round_time = seconds_to_minutes(time())

            self.n_players += 1
            start_new_thread(self.new_threaded_client, (connection,))

    def make_color(self):
        return f"(color int:{self.n_players % len(COLORS)})"


server = Server()
server.start_server()
