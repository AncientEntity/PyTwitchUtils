import json
from urllib.request import urlopen
import json
import re

MSG_OTHER = -1 #If the message is unidentified within PyTwitchUtils. Aka needs implementation.
MSG_CHAT = 0 #If the message is from a user
MSG_USERNOTICE = 1 #If the message is a twitch message, etc USERNOTICE
MSG_JOIN = 2 #If the message is a user joining.
MSG_USERSTATE = 3 #If the message is USERSTATE
MSG_WHISPER = 4 #A whisper recieved.

class Message:
    def __init__(self,rawData,currentChannel):
        self.raw = rawData
        #print(rawData)
        self.messageData = {}
        self.messageType = MSG_CHAT
        rawData = rawData[1:].split(";")
        for seg in rawData:
            final = seg.split("=")
            if (len(final) == 1):
                continue
            self.messageData[final[0]] = final[1]
        if('user-type' in self.messageData and 'display-name' in self.messageData and self.messageData['user-type'].find("PRIVMSG") != -1):
            self.messageData["message"] = self.messageData["user-type"][self.messageData["user-type"].find("PRIVMSG #")+len(currentChannel.name):].split(":")[1].replace('\r\n','')
        elif('user-type' in self.messageData):
            if("USERNOTICE" in self.messageData['user-type']):
                self.messageType = MSG_USERNOTICE
            elif("USERSTATE" in self.messageData['user-type']):
                self.messageType = MSG_USERSTATE
            elif("WHISPER" in self.messageData['user-type']):
                self.messageType = MSG_WHISPER
                self.messageData["message"] = self.messageData["user-type"][self.messageData["user-type"].find("WHISPER #") + len(currentChannel.name):].split(":")[1].replace('\r\n', '')
            else:
                Log("Unimplemented Message Came Through PyTwitchUtils: "+self.raw)
                self.messageType = MSG_OTHER
        else:
            if("JOIN" in self.raw):
                self.messageType = MSG_JOIN
                self.messageData['display-name'] = self.raw.split("!")[0][1:]
    @property
    def owner(self):
        return self.messageData["display-name"]
    @property
    def message(self):
        return self.content()
    @property
    def content(self):
        try:
            return self.messageData['message'] #probably preferably to message() since it'll be message.content instead of message.message
        except:
            return ""

    def GetMessage(self):
        return self.messageData["message"]
    def GetOwner(self):
        self.messageData["display-name"]
    def GetSubscriberInfo(self):
        """
        Returns the amount of months the owner has been subscribed.
        Returns -1 if not subscribed.
        """
        if("badge-info" in self.messageData):
            badges = self.messageData['badge-info'].split(',')
            for badge in badges:
                info = badge.split("/")
                if(info[0] == "subscriber"):
                    return int(info[1])
        return -1
    def GetBadges(self):
        finalOut = []
        if("badge-info" in self.messageData):
            badges = self.messageData['badge-info'].split(",")
            for badge in badges:
                finalOut.append(badge.split('/'))
        return finalOut
    def IsEmoteOnly(self):
        if("emote-only" in self.messageData and self.messageData['emote-only'] == '1'):
            return True
        return False
    def IsMod(self):
        if("badges" in self.messageData):
            if("moderator" in self.messageData['badges']):
                return True
        return False
    def IsBroadcaster(self):
        if("badges" in self.messageData):
            if("broadcaster" in self.messageData['badges']):
                return True
        return False
    def IsVIP(self):
        if("badges" in self.messageData):
            if("vip" in self.messageData['badges']):
                return True
        return False
    def IsReSub(self):
        if(self.messageType == MSG_USERNOTICE and "msg-id" in self.messageData):
            if(self.messageData['msg-id'] == 'resub'):
                return True
        return False
    def IsSubscribe(self,includeResub=True):
        if (self.messageType == MSG_USERNOTICE and "msg-id" in self.messageData):
            if (self.messageData['msg-id'] == 'resub' or (self.messageData['msg-id'] == 'sub' and includeResub)):
                return True
        return False

class Command:
    def __init__(self,trigger,onTriggerEvents,prefix=""):
        self.prefix = prefix #Something like '!', for like !ping. However it may be better to include it directly in the trigger.
        self.trigger = trigger #So like 'ping'
        self.onTriggered = onTriggerEvents #A list (or 1) method that'll get called, being passed a 'CommandArgs' object.
        self.caseSensitive = False
        self.vipOnly = False
        self.modOnly = False
        self.broadcasterOnly = False
    def CheckForCommand(self,message):
        if(self.broadcasterOnly and message.IsBroadcaster() == False):
            return
        if(self.modOnly and message.IsMod() == False):
            return
        if(self.vipOnly and message.IsVip() == False):
            return


        splitUp = message.content.lower().split(" ")
        if(splitUp[0] == self.prefix+self.trigger):
            #Must be my command!
            splitUp.pop(0)
            if(isinstance(self.onTriggered,list)):
                for event in self.onTriggered:
                    event(CommandArgs(message.owner,splitUp,message))
            else:
                self.onTriggered(CommandArgs(message.owner,splitUp,message))

class CommandArgs:
    def __init__(self, owner, args, message):
        self.owner = owner
        self.args = args
        self.message = message

class Channel:
    def __init__(self,name):
        self.name = name # Channel's name
    def GetCurrentViewers(self):
        res = urlopen("https://tmi.twitch.tv/group/user/" + self.name + "/chatters")
        content = res.read()
        # print(List)

        totalChatters = []
        sortedChatters = json.loads(content)['chatters']
        for group in sortedChatters.keys():
            for chatter in sortedChatters[group]:
                totalChatters.append(chatter)
        return totalChatters
    def GetViewerGroup(self,group):
        res = urlopen("https://tmi.twitch.tv/group/user/" + self.name + "/chatters")
        content = res.read()
        # print(List)

        totalChatters = []
        return json.loads(content)['chatters'][group]
    def GetCurrentModerators(self):
        return self.GetViewerGroup('moderators')
    def GetCurrentVIPs(self):
        return self.GetViewerGroup('vips')
    def GetViewerCount(self):
        res = urlopen("https://tmi.twitch.tv/group/user/" + self.name + "/chatters")
        content = json.loads(res.read())
        return int(content['chatter_count'])

def Log(msg):
    print("[PyTwitchUtils] "+msg)


if(__name__ == "__main__"):
    from bot import *
