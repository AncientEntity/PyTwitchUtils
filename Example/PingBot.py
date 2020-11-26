from bot import TwitchBot
from main import Command

#Check line 6, and 22 to make it work. Good day sir and have fun!

bot = TwitchBot("TWITCH USERNAME", "OAUTH HERE")


def OnJoinTest():
    print("Welcome Message Sent!")
    bot.Chat("Hello! I have arrived to moderate the universe!")


def PingCommand(cArgs):
    print("Ponged.")
    bot.Chat("@" + cArgs.owner + " Pong!")


bot.RegisterCommand(Command("!ping", PingCommand))

bot.onJoinEvents.append(OnJoinTest)
bot.Connect("CHANNEL TO CONNECT TO")

while True:
    message = bot.GetNext()
    #print(message.IsMod())
    #print(message.IsBroadcaster())
