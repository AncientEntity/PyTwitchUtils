from PyTwitchUtils import panelbot
from PyTwitchUtils.bot import *

bot = panelbot.PanelBot()

def OnJoinTest():
    print("Welcome Message Sent!")
    #bot.twitchBot.Chat("Hello! I have arrived to moderate the universe!")

def OnSubscribe(message):
    print(message.owner + " has subscribed!")

def OnUserJoin(username):
    print(username + " has joined the chat.")

def PingCommand(cArgs):
    print("Ponged.")
    #bot.Chat("@" + cArgs.owner + " Pong!")

bot.twitchBot.RegisterCommand(Command("!ping", PingCommand))

bot.twitchBot.onStartEvents.append(OnJoinTest)
bot.twitchBot.onSubscribeEvents.append(OnSubscribe)
bot.twitchBot.onJoinChatEvents.append(OnUserJoin)


while True:
    bot.Tick()