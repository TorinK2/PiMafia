import socket


# Handles server functionality to send information between server and client
class Server:
    def __init__(self):
        # Gets port
        self.port = int(input("Enter port: "))
        self.initial_connection = 0
        self.client_sockets = []
        self.setup_socket()

    # Sets up socket to receive client connections
    def setup_socket(self):
        self.socket = socket.socket()
        self.socket.bind(('0.0.0.0', self.port))

    # Connects to a single client
        # Adds client to self.client_sockets
    def connect(self):
        self.socket.listen(5)
        c, addr = self.socket.accept()
        client_manager = ClientManager(c, addr)
        self.client_sockets.append(client_manager)
        print("CONNECTED")
        return client_manager

    # Allows indexing of object to reference specific ClientManager objects
    def __getitem__(self, key):
        return self.client_sockets[key]

    # Property to get initial ClientManager created (first connected client)
    @property
    def initial_client(self):
        if len(self.client_sockets) == 0:
            raise Exception("No initial client has been connected.")
        else:
            return self[0]


# Handles server interactions with a single client
class ClientManager:
    def __init__(self, c, addr):
        self.socket = c
        self.address = addr

    # Receives a message from the client
    def receive(self):
        r = self.socket.recv(1024).decode()
        print("Receiving: " + r)
        return r

    # Sends a message to the client
    def send(self, mssg):
        print("Sending: " + mssg)
        self.socket.send(mssg.encode())

    # Sends message to client and receives/returns feedback from client
    def ask(self, mssg):
        self.send(mssg)
        return self.receive()


# Test of Server and ClientManager classes' functionality:
if __name__ == '__main__':
    test_server = Server()
    test_server.connect()
    print(test_server.initial_client.ask("Question: "))
