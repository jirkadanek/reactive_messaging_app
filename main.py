#!/usr/bin/env python2
import threading
from multiprocessing import Queue
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

import time

import proton
from proton.reactor import Container, AtMostOnce
from proton.handlers import MessagingHandler


class ChatWindow(object):
    def __init__(self, root):
        self.root = root

        frame = Frame(root)
        frame.pack()

        self.chatlog = Text(frame)
        self.chatlog.pack()

        self.input = Frame(frame)
        self.input.pack()

        self.field_var = StringVar()
        self.field = Entry(self.input, textvariable=self.field_var)
        self.field.pack(side=LEFT)

        self.button = Button(self.input, text="Send", command=self.send_message, state=DISABLED)
        self.button.pack(side=LEFT)

        self.messenger = None

    def inject_messenger(self, messenger):
        self.receive_message('Welcome to Chat for All!')
        self.button.configure(state=NORMAL)
        self.messenger = messenger

    def send_message(self):
        self.messenger.send_message(self.field_var.get())
        self.field_var.set("")

    def receive_message(self, message):
        self.chatlog.insert(END, time.strftime("%H:%M:%S") + ': ' + message + '\n')
        self.root.update()


class ChatMesssenger(MessagingHandler):
    def __init__(self, gui, sender_address, receiver_address):
        super(ChatMesssenger, self).__init__()
        self.gui = gui
        self.sender_address = sender_address
        self.receiver_address = receiver_address

        self.sender = None

        self.ready_to_send = False
        self.outgoing_queue = Queue()

    def on_start(self, event):
        print('on_start')
        event.container.create_receiver(self.receiver_address)
        event.container.create_sender(self.sender_address, options=AtMostOnce())

    def on_sendable(self, event):
        print('on_sendable')
        self.sender = event.sender
        self.ready_to_send = True
        self.send_messages()
        # TODO: ??? I cannot send my messages from on_sendable because I do not always have something to send here
        # and if I miss one on_sendable and do not send anything, it will not be called again the next time

    def on_message(self, event):
        print("on_message")
        self.gui.receive_message(str(event.message.body))

    def send_messages(self):
        if not self.ready_to_send:
            return

        while self.sender.credit:
            if self.outgoing_queue.empty():
                return
            message = proton.Message()
            body = self.outgoing_queue.get()
            message.body = body
            self.sender.send(message)

            self.ready_to_send = False

    def send_message(self, body):
        self.outgoing_queue.put(body)
        self.send_messages()


class GuiThread(threading.Thread):
    def __init__(self, initialized_event):
        super(GuiThread, self).__init__()
        self.gui_initialized_event = initialized_event
        self.chat_window = None

    def run(self):
        root = Tk()
        self.chat_window = ChatWindow(root)
        self.gui_initialized_event.set()
        root.mainloop()


class MessagingThread(threading.Thread):
    def __init__(self, router_address, initialized, gui):
        self.router_address = router_address
        self.initialized = initialized
        self.gui = gui

        self.m = None
        self.r = None
        super(MessagingThread, self).__init__()

    def run(self):
        self.m = ChatMesssenger(self.gui,
                                sender_address=self.router_address,
                                receiver_address=self.router_address)

        self.r = Container(self.m)
        self.m.container = self.r
        self.initialized.set()
        self.r.run()


def main():
    """GUI and Proton reactor are two separate threads"""
    router_address = sys.argv[1]

    gui_initialized = threading.Event()
    messenger_initialized = threading.Event()

    gui = GuiThread(gui_initialized)
    gui.start()
    gui_initialized.wait()

    messenger = MessagingThread(router_address, messenger_initialized, gui.chat_window)
    messenger.start()
    messenger_initialized.wait()

    gui.chat_window.inject_messenger(messenger.m)

    gui.join()
    print("joined gui")

    # TODO: Is this the correct way to stop a Reactor from the outside?
    messenger.r.stop()
    messenger.join()
    print("joined messenger")


if __name__ == '__main__':
    main()
