from const import *
from protocol import MessageProtocol, ConnectionBroken

from datetime import datetime
import socket
import threading

class Message():
    """ Keeps track of contents of a message and metadata (username, time)"""
    def __init__(self, usertag, timestamp, message):
        self.usertag = usertag
        self.timestamp = timestamp
        self.message = message

    def __str__(self):
        return "[{:02d}:{:02d}:{:02d}]{}:{}".format(
            self.timestamp.hour,
            self.timestamp.minute,
            self.timestamp.second,
            self.usertag,
            self.message
        )

class Server(threading.Thread):
    """
    Allows for running the server inside a separate thread. Starts more threads
    for each client connection.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.messages = []
        self.messages_lock = threading.Lock()
        self.socket = socket.socket()
        self.running = False

    def get_new_messages(self, previous_index):
        """
        Safely returns messages received from all clients to a particular client
        thread.

        Parameters:
        previous_index (int): The index of the newest message that was acquired by
                        the client
        """
        with self.messages_lock:
            out = "\n".join([str(m) for m in self.messages[previous_index:]])
            new_index = len(self.messages)
        return out, new_index

    def client_thread(self, connection, ip):   
        """
        Communicates with one client
        
        Parameters:
        connection: socket wrapped inside the MessageProtocol class,
        ip: The IP address of the connected client
        """
        try:            
            username = connection.get_message()
            usertag = "{}@{}".format(username, ip)
            # Keeps track of the newest message that was sent out to the client
            message_counter = 0
        
            joined_message = "{} has joined the chat.".format(usertag)
            self.messages.append(Message("Server", datetime.now(), joined_message))                             
            
            while True:
                # Send new messages to the client
                data_to_send, message_counter = self.get_new_messages(message_counter)
                if data_to_send:
                    connection.send_message(data_to_send)
                else:
                    connection.ping()

                # Receive new messages from the client
                received_data = connection.get_message()
                if received_data:           
                    self.messages.append(Message(usertag, datetime.now(), received_data))                                
        except ConnectionBroken as e:
            connection.terminate()
            print("Client disonnected with error {}".format(str(e)))

    def run(self):
        """
        Overwrites threading.Thread.run, continuously acquires new connections
        with clients and starts threads for each one.
        """
        self.running = True
        try:
            self.socket.bind((SERVER_HOST, SERVER_PORT))
            self.socket.listen()
        except OSError as e:                        
            print ("Cannot connect to port {}. Error: {}.".format(SERVER_PORT, str(e)))
            return

        connections = []
        threads = []    
        while True:            
            client_socket, address = self.socket.accept()
            ip = address[0]
            if not self.running:
                # Loop needs to be stopped here in case of Ctrl+C
                # so new thread isn't created for no reason
                break  
            connection = MessageProtocol(client_socket)
            connections.append(connection)

            thread = threading.Thread(target=self.client_thread, args=(connection, ip))
            threads.append(thread)
            thread.start()                

        # Clean up code
        for connection in connections:
            connection.terminate()        
        self.socket.close()        

        for thread in threads:
            thread.join()

        
    def stop(self):
        """ Stops the server."""
        self.running = False
        
        # Make a fake connection to stop blocking on socket.accept
        # and be able to stop the server
        with socket.socket() as s:
            s.connect((CLIENT_CONNECTION_POINT, SERVER_PORT))


if __name__ == "__main__":
    import signal
    import sys

    server = Server()
    server.start()    

    def shutdown_handler(sig, frame):
        print("Server exit with Ctrl+C")
        server.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, shutdown_handler)
    
    print("Press Ctrl+C to quit")
    while True: pass #Wait for Ctrl+C
