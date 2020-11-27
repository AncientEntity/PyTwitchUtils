from bot import TwitchBot
from main import Command

bot = TwitchBot("TWITCH BOT USERNAME", "TWITCH BOT OAUTH")


def OnJoinTest():
    print("Welcome Message Sent!")
    #bot.Chat("Hello! I have arrived to moderate the universe!")

def OnSubscribe(message):
    print(message.owner + " has subscribed!")

def OnUserJoin(username):
    print(username + " has joined the chat.")

def PingCommand(cArgs):
    print("Ponged.")
    #bot.Chat("@" + cArgs.owner + " Pong!")


bot.RegisterCommand(Command("!ping", PingCommand))

bot.onStartEvents.append(OnJoinTest)
bot.onSubscribeEvents.append(OnSubscribe)
bot.onJoinChatEvents.append(OnUserJoin)
bot.Connect("CHANNEL TO JOIN")

while True:
    message = bot.GetNextAny()
    if(message == None):
        continue
    print(str(message.messageType) + " "+str(message.messageData))