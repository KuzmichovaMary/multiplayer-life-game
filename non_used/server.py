import json
import asyncio
import pickle

clients = []


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info(f"peername")
        print(f"Connection_made: {self.peername}")
        clients.append(self.transport)

    def to_pickle(self, data):
        return pickle.dumps(data)

    def from_pickle(self, data):
        return pickle.loads(data)

    def data_received(self, data):
        print(f"Data received: {self.from_pickle(data)}")
        self.send("Data received.", self.transport)
        self.broadcast(data)

    def send(self, message, transport):
        transport.write(message.encode())

    def broadcast(self, data):
        for client in clients:
            if client is not self.transport:
                client.write(data)

    def connection_lost(self, ex):
        print(f"Connection_lost: {self.peername}")
        clients.remove(self.transport)


SERVER_PORT = 8080

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ServerProtocol, '127.0.0.1', SERVER_PORT)
    server = loop.run_until_complete(coro)

    print(f'Serving on {server.sockets[0].getsockname()}')

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()