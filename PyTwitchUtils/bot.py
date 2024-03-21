import socket, time, threading, os, importlib

import PyTwitchUtils.panel
from .datatypes import Message, Channel, MSG_CHAT, MSG_JOIN, CommandArgs
from .datatypes import Command
from .datatypes import Log
from .channelconnection import *

class TwitchBot:
    def __init__(self,username,oauth):
        self.active = False
        self.username = username
        self.oauth = oauth
        if("oauth:" not in self.oauth):
            self.oauth = "oauth:" + oauth
        self.ignoreSelf = True

        self.__channelModules = [] #Imported modules for channels. Dont add directly without knowing what you are doing.

        self.onStartEvents = [] #Functions, will get ran on join. Gets Channel passed in.
        self.onSubscribeEvents = [] #When someone subscribers run these. PASSES THE USERNOTICE MESSAGE.
        self.onJoinChatEvents = [] #When someone joins the chat. Passes in the message.
        self.commandRegistry = [] #List of the registered commands.

        self.ircServer = ("irc.chat.twitch.tv",6667)
        self.messageSize = 4096

        self.channelConnections = {}
        self.messageQueue = {-1 : [], 0 : [], 1 : [], 2 : [], 3 : [], 4 : [], 5 : []} #key is the type of the message, value is the message.
        self.dontQueue = False
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
    def ConnectionManager(self,connection):
        Log("Bot manager has begun.")
        while self.active:
            recieved = self.RecieveMessage(connection)
            formattedMessage = Message(recieved,connection.channel)
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
                event(formattedMessage)
        if (self.dontQueue == False):
            self.messageQueue[formattedMessage.messageType].append(formattedMessage)
    def RegisterCommand(self,command):
        self.commandRegistry.append(command)
    def RecieveMessage(self,connection):
        waiting = True
        while(waiting):
            try:
                response = connection.socket.recv(self.messageSize).decode()
                #print(response)
                if (response == "PING :tmi.twitch.tv\r\n"):
                    self.SendMessage("PONG :tmi.twitch.tv\r\n")
                    Log("Successfully Pinged the server")
                elif ("End of /NAMES list" in response):
                    Log("Successfully Connected To " + connection.channel.name)
                    time.sleep(1.2)
                    Log("Welcome Message Successfully Send.")
                    time.sleep(0.5)
                    self.SendMessage("CAP REQ :twitch.tv/tags\r\n",connection.channel.name)
                    self.SendMessage("CAP REQ :twitch.tv/membership\r\n",connection.channel.name)
                    self.SendMessage("CAP REQ :twitch.tv/commands\r\n",connection.channel.name)
                    for event in self.onStartEvents:
                        event(connection.channel)
                else:
                    waiting = False

                if(waiting == False):
                    return response
            except:
                #Socket most likely closed
                return ""
    def SendMessage(self,msg,channelName):
        self.channelConnections[channelName].socket.send(msg.encode())
    def Connect(self,channelNames): #channelName or channel1,channel2,etc
        for channelToJoin in channelNames.split(","):
            newConnect = ChannelConnection()
            newConnect.socket.connect(self.ircServer)
            self.channelConnections[channelToJoin] = newConnect
            self.SendMessage("PASS "+self.oauth+"\r\n",channelToJoin)
            self.SendMessage("NICK "+self.username+"\r\n",channelToJoin)
            time.sleep(0.25)
            self.SendMessage("JOIN #"+channelToJoin+"\r\n",channelToJoin)
            newConnect.channel = Channel(channelToJoin)
            self.active = True
            self.LoadChannelConfig(newConnect.channel)
            newManagerThread = threading.Thread(target=self.ConnectionManager, args=(newConnect,))
            newConnect.managerThread = newManagerThread
            newManagerThread.start()
            print("Connected to: "+channelToJoin)
    def Close(self):
        self.active = False
        time.sleep(0.25) #Wait for managerThread to stop to prevent any possible issues
        for connection in self.channelConnections.values():
            connection.socket.close()
        for command in self.commandRegistry:
            if(command.deleteOnBotClose):
                self.commandRegistry.remove(command)
                Log("Cleaned up command: "+command.trigger+" for channel "+command.channelLimited)
    def Chat(self,msg,channelName):
        messageTemp = "PRIVMSG #" + channelName + " :" + msg
        self.SendMessage(messageTemp + "\r\n",channelName)
        PyTwitchUtils.panel.ConsoleWrite(PyTwitchUtils.panel.GenerateTimeStamp()+"<"+self.username+"> "+msg,'SkyBlue2')
    def CurriedChat(self, channelName):
        def _Chat(msg): #Curried functions have entered the chat??!!?!
            self.Chat(msg,channelName)
        return _Chat
    def Whisper(self,user, msg):
        messageTemp = "PRIVMSG #" + self.channel.name + " :/w "+user.lower()+" " + msg
        self.SendMessage(messageTemp + "\r\n")
    def Ban(self,user,reason=""): #Not Tested
        self.Chat("/ban "+user+" "+reason)
    def Timeout(self,user,secs=600): #Not Tested
        self.Chat("/timeout "+user+" "+str(secs))
    def LoadChannelConfig(self,channel : Channel):
        if (os.path.exists("configs") == False): #make sure config folder exists
            print("No config folder, generating one")
            os.mkdir("configs")

        if (False == os.path.exists("configs\\" + channel.name + ".py")):
            print(channel.name + " config file doesn't exist. generating one.")
            newConfig = open("configs\\" + channel.name + ".py", "w")
            newConfig.write(TwitchBotChannelConfig.templateConfig)
            newConfig.close()
        print("configs."+channel.name)
        channelConfig = importlib.import_module("configs." + channel.name)
        channelConfig.Init(TwitchBotChannelConfig(channel,self))
        for command in channelConfig.commands:
            command.channelLimited = channel.name
            command.deleteOnBotClose = True
            self.RegisterCommand(command)
            Log("Command Registered: " + command.trigger + " for channel: " + channel.name)
        Log("channel module ("+channel.name+") loaded.")
    def RegisterChannelModule(self,channelName,module):
        self.__channelModules[channelName] = module

class TwitchBotChannelConfig:
    templateConfig = """
import PyTwitchUtils

#AUTOGENERATED CONFIG FILE

commands = [] #This array will automatically get loaded, so put all the commands you want into here.

def Init(config : PyTwitchUtils.bot.TwitchBotChannelConfig): #Ran when you connect to the channel
    pass
"""
    def __init__(self,channel : Channel, bot : TwitchBot):
        self.bot = bot
        self.channel = channel
        self.Chat = bot.CurriedChat(channel.name)





