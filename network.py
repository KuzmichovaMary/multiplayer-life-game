import socket
from config import *


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())
        self.port = PORT
        self.addr = (self.server, self.port)
        self.color = self.connect()

    def get_pos(self):
        return self.color

    def connect(self):
        try:
            self.socket.connect(self.addr)
            return self.socket.recv(BUFF_SIZE).decode()
        except:
            pass

    def send(self, data, res=False):
        try:
            self.socket.send(str.encode(data))
            if res:
                return self.socket.recv(BUFF_SIZE)
        except socket.error as e:
            print(e)
