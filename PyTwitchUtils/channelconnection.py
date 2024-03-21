import socket

from PyTwitchUtils.datatypes import Channel


class ChannelConnection:
    def __init__(self):
        self.channel : Channel = None
        self.socket = socket.socket()
        self.managerThread = None
        self.dontQueue = False
