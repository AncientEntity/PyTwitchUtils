
class Message:
    def __init__(self,rawData):
        self.messageData = {}
        rawData = rawData[1:].split(";")
        for seg in rawData:
            final = seg.split("=")
            if (len(final) == 1):
                continue
            self.messageData[final[0]] = final[1]
        if('user-type' in self.messageData):
            self.messageData["message"] = self.messageData["user-type"][self.messageData["user-type"].find("#")+len(self.messageData["display-name"])+2:].replace('\r\n','')

def Log(msg):
    print("[PyTwitchUtils] "+msg)















if(__name__ == "__main__"):
    from bot import *

