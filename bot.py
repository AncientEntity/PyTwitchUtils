import socket, time, threading
from main import Message
from main import Log

class TwitchBot:
    def __init__(self,username,oauth):
        self.active = False
        self.username = username
        self.oauth = oauth
        self.socket = socket.socket()
        self.ircChannel = ("irc.chat.twitch.tv",6667)
        self.messageSize = 1024

        self.managerThread = None
        self.messageQueue = []
        self.channelIn = ""
    def GetNext(self):
        while(len(self.messageQueue) <= 0):
            pass #Hang until a message is ready
        next = self.messageQueue[0]
        self.messageQueue.pop(0)
        return next
    def BotManager(self):
        Log("Bot manager has begun.")
        while self.active:
            recieved = self.RecieveMessage()
            formattedMessage = Message(recieved)
            if(formattedMessage.messageData != {}):
                self.messageQueue.append(formattedMessage)
    def RecieveMessage(self):
        waiting = True
        while(waiting):
            response = self.socket.recv(self.messageSize).decode()

            if (response == "PING :tmi.twitch.tv\r\n"):
                self.SendMessage("PONG :tmi.twitch.tv\r\n")
                Log("Successfully Pinged the server")
            elif ("End of /NAMES list" in response):
                Log("Successfully Connected To " + self.channelIn)
                time.sleep(1.2)
                self.Chat("Twitch/Discord Relay Bot has arrived!")
                Log("Welcome Message Successfully Send.")
                time.sleep(0.5)
                self.SendMessage("CAP REQ :twitch.tv/tags\r\n")
                Log("Requesting User Data/Tags")
            else:
                waiting = False

            if(waiting == False):
                return response
    def SendMessage(self,msg):
        self.socket.send(msg.encode())
    def Connect(self,channelToJoin):
        self.socket.connect(self.ircChannel)
        self.SendMessage("PASS "+self.oauth+"\r\n")
        self.SendMessage("NICK "+self.username+"\r\n")
        time.sleep(0.5)
        self.SendMessage("JOIN #"+channelToJoin+"\r\n")
        self.channelIn = channelToJoin
        self.active = True
        self.managerThread = threading.Thread(target=self.BotManager,args=())
        self.managerThread.start()
    def Close(self):
        self.active = False
        time.sleep(0.25) #Wait for managerThread to stop to prevent any possible issues
        self.socket.close()
    def Chat(self,msg):
        messageTemp = "PRIVMSG #" + self.channelIn + " :" + msg
        self.SendMessage(messageTemp + "\r\n")
    def DoPing(self):
        self.SendMessage("PONG :tmi.twitch.tv\r\n")

