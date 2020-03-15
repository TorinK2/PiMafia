import socket


# Handles client functionality to send information between server and client
class Client():
    def __init__(self):
        # Gets port and IP address of server
        self.port = int(input("Enter port: "))
        self.ip = str(input("Enter server IP: "))
        self.setup_socket()

    # Sets up socket to connect to server
    def setup_socket(self):
        self.socket = socket.socket()

    # Connects to the server
    def connect(self):
        self.socket.connect((self.ip, self.port))
        print("CONNECTED")

    # Sends a message to the server
    def send(self, mssg):
        self.socket.send(mssg.encode())

    # Receives a message from the server
    def receive(self):
        r = self.socket.recv(1024).decode()
        return r


# Test of Client class functionality:
if __name__ == '__main__':
    test_client = Client()
    test_client.connect()
    print(test_client.receive())
    test_client.send("Response")
