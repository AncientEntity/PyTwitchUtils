import json
from urllib.request import urlopen
import json

class Message:
    def __init__(self,rawData):
        self.raw = rawData
        self.messageData = {}
        rawData = rawData[1:].split(";")
        for seg in rawData:
            final = seg.split("=")
            if (len(final) == 1):
                continue
            self.messageData[final[0]] = final[1]
        if('user-type' in self.messageData):
            self.messageData["message"] = self.messageData["user-type"][self.messageData["user-type"].find("PRIVMSG #")+len(self.messageData["display-name"]):].split(":")[1].replace('\r\n','')

    @property
    def owner(self):
        return self.messageData["display-name"]
    @property
    def message(self):
        return self.messageData['message']
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
