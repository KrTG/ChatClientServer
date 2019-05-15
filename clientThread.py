from const import *

from protocol import MessageProtocol, ConnectionBroken

import socket
import threading
import queue

class ClientThread(threading.Thread):    
    """
    Facilitates communication with the server inside a separate thread. 
    The messages received by the client can be aquired by registering observers
    (Client.add_observer). Observers need to have a notify method takes 1 argument
    through which newly received messages will be passed.
    """
     
    def __init__(self, username):
        threading.Thread.__init__(self)
        self.username = username
        self.observers = []        
        self.connection = None
        self.thread = None
        self.message_queue = queue.Queue()

    def run(self):
        """
        Overwrites threading.Thread.run, makes a connection to the server, then
        receives and sends messages in a loop inside a thread
        """
        try:
            opened_socket = socket.socket()
            opened_socket.connect((CLIENT_CONNECTION_POINT, SERVER_PORT))            
            self.connection = MessageProtocol(opened_socket)
        except OSError as e:
            self._notify_observers(["Unable to connect to {}:{}. {}"
                .format(CLIENT_CONNECTION_POINT, SERVER_PORT, str(e))])
            return

        try:            
            self.connection.send_message(self.username)            
            while True:
                received_data = self.connection.get_message()                
                if received_data:
                    messages = received_data.split("\n")
                    self._notify_observers(messages)                
                try:
                    self.connection.send_message(self.message_queue.get(timeout=PING_DELAY))
                except queue.Empty:
                    self.connection.ping()

        except ConnectionBroken as e:
            self.connection.terminate()
            self._notify_observers(["Client disonnected with error {}".format(str(e))])            

    def stop(self):
        """
        Stops the socket connection, in effect also stopping the thread.
        """
        if self.connection:
            self.connection.terminate()

    def send_message(self, message):
        """
        Queues up a message to send to the server.

        Parameters:
        message (str): A message to send
        """
        self.message_queue.put(message)

    def add_observer(self, observer):
        """
        Adds an observer that will be notified when new messages from the server
        arrive

        Parameters:
        observer: An object with a 'notify' method
        """
        self.observers.append(observer)

    def _notify_observers(self, new_messages):
        """
        Notifies all observers

        Parameters:
        new_messages (list): List of new messages
        """
        for observer in self.observers:
            try:
                observer.notify(new_messages)            
            except Exception:
                pass
                # If observer raises some kind of exception
                # just ignore it
                    