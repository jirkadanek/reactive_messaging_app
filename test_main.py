from __future__ import print_function
from __future__ import unicode_literals

from threading import Thread

import time
from proton.reactor import Container
from unittest import TestCase

from main import ChatMesssenger


class MockGui(object):
    def __init__(self):
        self.received_messages = list()

    def receive_message(self, message):
        self.received_messages.append(message)


class MainTest(TestCase):
    def test_sending_and_receiving_messages(self):
        received_messages = set()

        gui = MockGui()

        a = '127.0.0.1/someaddress'
        m = ChatMesssenger(gui, a, a)

        c = Container(m)
        t = Thread(target=c.run)
        t.start()

        for i in range(10):
            m.send_message(str(i))
            time.sleep(1)
            print(gui.received_messages)

        c.stop()

        print(gui.received_messages)


