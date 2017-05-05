# reactive_messaging_app

Chat for All is a trivial chat room program written in Python 2 using the TK GUI library and Qpid Proton AMQP binding for Python. It uses a Qpid Dispatch Router as a backend. All instances of the app connect to a Qpid Dispatch Router and send and receive messages to/from the same multicast address.

## Usage

Have a Qpid Dispatch Router running and have at least one multicast address configured in it.

Run `python main.py 127.0.0.1/multicastaddress` to connect to locally running Qpid Dispatch Router to chat room at multicastaddress.

## Purpose

This app attempts to illustrate what a larger application that productively uses the AMQP Qpid Proton Binding might look like. There are two event loops (one for the GUI library and one for Qpid Proton) and they have to interoperate.

### Architecture

It sounds arrogant, as if I have it all figured out. Which is far from true. In fact . How do I shut down a reactor when it is ready to be shut down? How do I send a message not when the library is ready, but when I do have something to send.
