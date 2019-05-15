import socket

class ConnectionBroken(RuntimeError):    
    pass

class MessageProtocol():
    """ Wraps the socket protocol to communicate in messages varying in length"""
    def __init__(self, socket, buffer_size=2**11,
                 delimiter="<<END>>", ping_tag="<<PING>>", encoding="UTF-8"):
        """
        Parameters:
        socket (socket.socket): connected socket.
        buffer_size (int): Should be a power of 2. Socket buffer size.
        delimiter (str): A tag placed at the end of messages when sending.
        ping_tag (str): A tag signifying that this side of the connection is still respoding.
        encoding (str): Message encoding.
        """
        self.socket = socket
        self.buffer_size = buffer_size
        self.delimiter = delimiter
        self.ping_tag = ping_tag
        self.encoding = encoding

    def get_message(self):
        """Reads a message through the socket"""
        try:
            message = ""
            while not message.endswith(self.delimiter):
                partial = self.socket.recv(self.buffer_size)
                if len(partial) == 0:                
                    raise ConnectionBroken("Connection Stopped")
                message += partial.decode(self.encoding)

            message = message[:-len(self.delimiter)]
            if message == self.ping_tag:
                return None
            return message

        except OSError as e:
            raise ConnectionBroken(e)

    def send_message(self, message):
        """
        Sends a message through the socket

        Parameters:
        message (str): The message to send
        """
        try:
            self.socket.sendall(bytes(message + self.delimiter, encoding=self.encoding))
        except OSError as e:
            raise ConnectionBroken(e)

    def ping(self):
        """
        Sends a ping message to inform the other side that the connection is alive.
        """
        self.send_message(self.ping_tag)

    def terminate(self):
        """ Terminates the connection. """
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            # If its already closed ignore it
            pass
        self.socket.close()