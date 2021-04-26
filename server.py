import socket
from _thread import start_new_thread
import sys
import pickle
from life import Life
from time import time
from config import *


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


MY_IPV4 = "192.168.1.150"
HOST = socket.gethostbyname(socket.gethostname())
SEND = True
NOT_SEND = False


life = Life()
scores = {}


class TimeManager:
    def __init__(self):
        self.placing_cells_time = ROUND_TIME
        self.eating_time = EATING_TIME
        self.show_info_time = SHOW_INFO_TIME

        self.start_placing_cells_time = None
        self.start_eating_time = None
        self.start_show_info_time = None

        self.n_players = 0
        self.rounds_passed = 0

        self.placing_cells_mode = False
        self.showing_info_mode = False
        self.eating_mode = False

    def start(self):
        self.start_placing_cells_time = time()
        self.placing_cells_mode = True

    def start_new_round(self):
        global life
        if self.showing_info_mode and time() - self.start_show_info_time > self.show_info_time:
            life = Life()
            self.showing_info_mode = False
            self.eating_mode = False
            self.placing_cells_mode = True
            self.start_placing_cells_time = time()

    def start_showing_info(self):
        if self.eating_mode and time() - self.start_eating_time > self.eating_time:
            self.showing_info_mode = True
            self.eating_mode = False
            self.placing_cells_mode = False
            self.start_show_info_time = time()
            self.update_scores()

    @staticmethod
    def update_scores():
        global scores
        for color_id in scores:
            scores[color_id] += life.calculate_cells_by_color(color_id)

    def start_eating(self):
        if self.placing_cells_mode and time() - self.start_placing_cells_time > self.placing_cells_time:
            self.showing_info_mode = False
            self.eating_mode = True
            self.placing_cells_mode = False
            self.start_eating_time = time()

    def what_now(self):
        self.start_showing_info()
        self.start_eating()
        self.start_new_round()
        if self.placing_cells_mode:
            return "place_cells"
        elif self.eating_mode:
            return "eat"
        elif self.showing_info_mode:
            return "show_info"


class EventManager:
    def __init__(self):
        self.n_players = 0
        self.key_client = 1
        self.players = []
        self.time_manager = TimeManager()

    def on_new_connection(self):
        self.n_players += 1
        if self.n_players == self.key_client:
            self.time_manager.start()
        self.players.append(self.n_players)
        scores[self.n_players] = 0

    def on(self, data):
        cmd, args = read_data(data)
        if cmd == "get_alive":
            return True, pickle.dumps(life.alive)
        elif cmd == "get_scores":
            return True, pickle.dumps(scores)
        elif cmd == "bounding_box":
            return True, pickle.dumps(life.bounding_box())
        elif cmd == "advance":
            life.advance()
            return True, pickle.dumps(life.alive)
        elif cmd == "toggle":
            x, y, color = args
            life.toggle(x, y, color)
            return False, None
        elif cmd == "what_now?":
            return True, self.time_manager.what_now().encode()
        elif cmd == "test_message":
            return True, b"-------------------------------- Hello client -----------------------------------"

    def make_color(self):
        return f"(color int:{self.n_players % len(COLORS)})"

    def on_connection_lost(self, color_id):
        global scores
        print(self.players, color_id)
        del scores[color_id]
        self.players.remove(color_id)
        if not self.players:
            sys.exit()
        self.key_client = self.players[0]


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_manager = EventManager()

    def new_threaded_client(self, connection):
        data = self.event_manager.make_color()
        color = read_data(data)[1][0]
        print(color, "COLOR")
        connection.sendall(data.encode())
        while True:
            try:
                data = connection.recv(BUFF_SIZE).decode()
                # print(f"Received: {data}")
                if not data:
                    # print("Disconnected.")
                    break
                do, message = self.event_manager.on(data)
                if do == SEND:
                    connection.sendall(message)
            except EOFError:
                print("Ran out of input.")

        print("Lost connection.")
        self.event_manager.on_connection_lost(color)
        connection.close()

    def start_server(self):
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as error:
            print(error)

        self.socket.listen(4)
        # print(f"Server started at {self.host} {self.port}")

        while True:
            connection, address = self.socket.accept()
            print(f"Connection with {address} established.")

            self.event_manager.on_new_connection()
            start_new_thread(self.new_threaded_client, (connection,))


server = Server()
server.start_server()
