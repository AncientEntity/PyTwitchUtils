import socket, time, threading
from main import Message, Channel
from main import Command
from main import Log

class TwitchBot:
    def __init__(self,username,oauth):
        self.active = False
        self.username = username
        self.oauth = oauth
        if("oauth:" not in self.oauth):
            self.oauth = "oauth:" + oauth
        self.socket = socket.socket()
        self.ircServer = ("irc.chat.twitch.tv", 6667)
        self.messageSize = 1024
        self.ignoreSelf = True

        self.onJoinEvents = [] #Functions, will get ran on join.
        self.commandRegistry = [] #List of the registered commands.

        self.managerThread = None
        self.messageQueue = []
        self.channel = None
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
            if("display-name" not in formattedMessage.messageData or (formattedMessage.owner == self.username and self.ignoreSelf)):
                continue #If self, ignore.
            for command in self.commandRegistry:
                command.CheckForCommand(formattedMessage)
            if(formattedMessage.messageData != {}):
                self.messageQueue.append(formattedMessage)
    def RegisterCommand(self,command):
        self.commandRegistry.append(command)
    def RecieveMessage(self):
        waiting = True
        while(waiting):
            response = self.socket.recv(self.messageSize).decode()
            #print(response)
            if (response == "PING :tmi.twitch.tv\r\n"):
                self.SendMessage("PONG :tmi.twitch.tv\r\n")
                Log("Successfully Pinged the server")
            elif ("End of /NAMES list" in response):
                Log("Successfully Connected To " + self.channel.name)
                time.sleep(1.2)
                Log("Welcome Message Successfully Send.")
                time.sleep(0.5)
                self.SendMessage("CAP REQ :twitch.tv/tags\r\n")
                Log("Requesting User Data/Tags")
                for event in self.onJoinEvents:
                    event()
            else:
                waiting = False

            if(waiting == False):
                return response
    def SendMessage(self,msg):
        self.socket.send(msg.encode())
    def Connect(self,channelToJoin):
        self.socket.connect(self.ircServer)
        self.SendMessage("PASS "+self.oauth+"\r\n")
        self.SendMessage("NICK "+self.username+"\r\n")
        time.sleep(0.5)
        self.SendMessage("JOIN #"+channelToJoin+"\r\n")
        self.channel = Channel(channelToJoin)
        self.active = True
        self.managerThread = threading.Thread(target=self.BotManager,args=())
        self.managerThread.start()
    def Close(self):
        self.active = False
        time.sleep(0.25) #Wait for managerThread to stop to prevent any possible issues
        self.socket.close()
    def Chat(self,msg):
        messageTemp = "PRIVMSG #" + self.channel.name + " :" + msg
        self.SendMessage(messageTemp + "\r\n")
    def Ban(self,user,reason=""): #Not Tested
        self.Chat("/ban "+user+" "+reason)
    def Timeout(self,user,secs=600): #Not Tested
        self.Chat("/timeout "+user+" "+str(secs))







