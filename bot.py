import socket, time, threading
from main import Message, Channel, MSG_CHAT, MSG_JOIN
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
        self.messageSize = 4096
        self.ignoreSelf = True

        self.onStartEvents = [] #Functions, will get ran on join.
        self.onSubscribeEvents = [] #When someone subscribers run these. PASSES THE USERNOTICE MESSAGE
        self.onJoinChatEvents = [] #When someone joins the chat.
        self.commandRegistry = [] #List of the registered commands.

        self.managerThread = None
        self.messageQueue = {-1 : [], 0 : [], 1 : [], 2 : [], 3 : [], 4 : [], 5 : []} #key is the type of the message, value is the message.
        self.dontQueue = False
        self.channel = None

    def GetNext(self): #Get's the next PRIVMSG in the queue
        return self.GetNextOfType(MSG_CHAT)
    def GetNextOfType(self,msgType):
        if(self.dontQueue):
            print("Trying to GetNextOfType() while dontQueue is equal to True. The queue will never get anything while it is True.")
            return
        while(len(self.messageQueue[msgType]) <= 0):
            pass #Hang until a message is ready
        next = self.messageQueue[msgType][0]
        self.messageQueue[msgType].pop(0)
        return next
    def GetNextAny(self) -> Message:
        for key in self.messageQueue.keys():
            if(len(self.messageQueue[key]) > 0):
                next = self.messageQueue[key][0]
                self.messageQueue[key].pop(0)
                return next
        return None
    def BotManager(self):
        Log("Bot manager has begun.")
        while self.active:
            recieved = self.RecieveMessage()
            if(recieved == ""): continue;
            formattedMessage = Message(recieved,self.channel)
            self.HandleMessage(formattedMessage)
    def HandleMessage(self,formattedMessage):
        if ("display-name" in formattedMessage.messageData and formattedMessage.owner == self.username and self.ignoreSelf):
            return
        for command in self.commandRegistry:
            command.CheckForCommand(formattedMessage)
        if (formattedMessage.IsSubscribe()):
            for event in self.onSubscribeEvents:
                event(formattedMessage)
        if (formattedMessage.messageType == MSG_JOIN):
            for event in self.onJoinChatEvents:
                event(formattedMessage.owner)
        if (self.dontQueue == False):
            self.messageQueue[formattedMessage.messageType].append(formattedMessage)
    def RegisterCommand(self,command):
        self.commandRegistry.append(command)
    def RecieveMessage(self):
        waiting = True
        while(waiting):
            try:
                response = self.socket.recv(self.messageSize).decode()
            except:
                return "" #Socket was closed mid recv
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
                self.SendMessage("CAP REQ :twitch.tv/membership\r\n")
                self.SendMessage("CAP REQ :twitch.tv/commands\r\n")
                for event in self.onStartEvents:
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
        time.sleep(0.25)
        self.SendMessage("JOIN #"+channelToJoin+"\r\n")
        self.channel = Channel(channelToJoin)
        self.active = True
        self.managerThread = threading.Thread(target=self.BotManager,args=())
        self.managerThread.start()
    def Close(self):
        self.active = False
        time.sleep(0.25) #Wait for managerThread to stop to prevent any possible issues
        self.socket.close()
        self.socket = socket.socket()
    def Chat(self,msg):
        messageTemp = "PRIVMSG #" + self.channel.name + " :" + msg
        self.SendMessage(messageTemp + "\r\n")
        PyTwitchUtils.panel.ConsoleWrite(PyTwitchUtils.panel.GenerateTimeStamp()+"<"+self.username+"> "+msg,'SkyBlue2')
    def Whisper(self,user, msg):
        messageTemp = "PRIVMSG #" + self.channel.name + " :/w "+user.lower()+" " + msg
        self.SendMessage(messageTemp + "\r\n")
    def Ban(self,user,reason=""): #Not Tested
        self.Chat("/ban "+user+" "+reason)
    def Timeout(self,user,secs=600): #Not Tested
        self.Chat("/timeout "+user+" "+str(secs))

