
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
            self.messageData["message"] = self.messageData["user-type"][self.messageData["user-type"].find("#")+len(self.messageData["display-name"])+3:].replace('\r\n','')

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

class Command:
    def __init__(self,trigger,onTriggerEvents,prefix=""):
        self.prefix = prefix #Something like '!', for like !ping. However it may be better to include it directly in the trigger.
        self.trigger = trigger #So like 'ping'
        self.onTriggered = onTriggerEvents #A list (or 1) method that'll get called, being passed a 'CommandArgs' object.
        self.caseSensitive = False
    def CheckForCommand(self,message):
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


def Log(msg):
    print("[PyTwitchUtils] "+msg)















if(__name__ == "__main__"):
    from bot import *

