import protocol
import server
import client

import unittest
import socket
import random

class TestProtocol(unittest.TestCase):
    def setUp(self):        
        socket1, socket2 = socket.socketpair()
        self.connection1 = protocol.MessageProtocol(socket1)
        self.connection2 = protocol.MessageProtocol(socket2)        

    def tearDown(self):
        self.connection1.terminate()
        self.connection2.terminate()

    def test_empty(self):
        self.connection1.send_message("")
        self.assertEqual(self.connection2.get_message(), "")

    def test_communication(self):
        self.connection1.send_message("Hello")
        self.assertEqual(self.connection2.get_message(), "Hello")
        self.connection2.send_message("Hi")
        self.assertEqual(self.connection1.get_message(), "Hi")
        self.connection1.send_message("привет")
        self.assertEqual(self.connection2.get_message(), "привет")
        self.connection2.send_message("привет")
        self.assertEqual(self.connection1.get_message(), "привет")

    def test_long_messages(self):
        random1 = "".join(chr(random.randint(32, 126)) for _ in range(2**11+1))
        random2 = "".join(chr(random.randint(32, 126)) for _ in range(2**13+1))
        random3 = "".join(chr(random.randint(32, 126)) for _ in range(2**15+1))
        self.connection1.send_message(random1)
        self.assertEqual(self.connection2.get_message(), random1)
        self.connection2.send_message(random2)
        self.assertEqual(self.connection1.get_message(), random2)
        self.connection1.send_message(random3)
        self.assertEqual(self.connection2.get_message(), random3)

    def test_escaping_special(self):
        self.connection1.send_message("<<PING>>")
        self.assertEqual(self.connection2.get_message(), "")
        self.connection2.send_message("<<END>>")
        self.assertEqual(self.connection1.get_message(), "")

    def test_terminate(self):
        self.connection1.terminate()
        self.connection2.terminate()
        self.connection2.terminate()

        with self.assertRaises(protocol.ConnectionBroken):
            self.connection1.send_message("test")
        with self.assertRaises(protocol.ConnectionBroken):
            self.connection1.get_message()
        with self.assertRaises(protocol.ConnectionBroken):
            self.connection2.send_message("test")
        with self.assertRaises(protocol.ConnectionBroken):
            self.connection2.get_message()        

if __name__ == "__main__":
    unittest.main()