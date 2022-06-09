from bot import TwitchBot
from main import *
import panel

class PanelBot:
	"""A Twitch bot with a panel GUI."""
	def __init__(self):
		self.twitchBot = TwitchBot("","")
		self.chatFeedActive = True
		panel.SetConfigSetting("username", "")
		panel.SetConfigSetting("oauth", "")
		panel.SetConfigSetting("targetChannel", "")
		panel.CreatePanel()
		self.toggleChatButtonIndex = panel.CreateNewSettingsButton("Disable Chat Feed", self.ChatToggle)
		self.connectTwitchButtonIndex = panel.CreateNewSettingsButton("Connect to Twitch", self.ConnectToTwitch)

		self.messageQueue = {-1: [], 0: [], 1: [], 2: [], 3: [], 4: [],
							 5: []}  # key is the type of the message, value is the message.
	def Tick(self):
		panel.Tick()

		panelMessage = panel.GetNextCommandRaw()
		if (panelMessage != None and self.twitchBot.active):
			if(panelMessage[0] != "!"):
				self.twitchBot.Chat(panelMessage)

		if self.twitchBot.active:
			message = self.twitchBot.GetNextAny()
			if (message == None):
				return
			else:
				self.messageQueue[message.messageType].append(message)
				if self.chatFeedActive and message.messageType == MSG_CHAT:
					owner = message.owner
					if (owner != None):
						panel.ConsoleWrite(panel.GenerateTimeStamp() + "<" + owner + "> " + message.message,
										   color='blue')
	def ChatToggle(self):
		if (self.chatFeedActive):
			self.chatFeedActive = False
			panel.GetButtonByIndex(self.toggleChatButtonIndex)["text"] = "Enable Chat Feed"
			panel.ConsoleWrite("Chat Disabled", 'blue')
		else:
			self.chatFeedActive = True
			panel.GetButtonByIndex(self.toggleChatButtonIndex)["text"] = "Disable Chat Feed"
			panel.ConsoleWrite("Chat Enabled", 'blue')
	def ConnectToTwitch(self):
		panel.ReadConfigFile()

		if (self.twitchBot.active == True):
			self.twitchBot.Close()
			panel.ConsoleWrite("Bot disconnected from Twitch.", 'blue')
			panel.GetButtonByIndex(self.connectTwitchButtonIndex)["text"] = "Connect to Twitch"
			return
		if(panel.configSettings["username"] == "" or panel.configSettings["oauth"] == "" or panel.configSettings["targetChannel"] == "" or "oauth:" not in panel.configSettings["oauth"]):
			panel.ConsoleWrite("Incorrect Bot Credentials... Check Config",'red')
			return
		try:
			self.twitchBot.username = panel.configSettings["username"]
			self.twitchBot.oauth = panel.configSettings["oauth"]
			self.twitchBot.Connect(panel.configSettings["targetChannel"])
			panel.GetButtonByIndex(self.connectTwitchButtonIndex)["text"] = "Disconnect from Twitch"
		except Exception as e:
			panel.ConsoleWrite(str(e), 'red')
			panel.ConsoleWrite(
				"Try restarting the bot, that usually works. Otherwise you have incorrect credentials in the config or an antivirus/firewall is blocking the connection.",
				'red')
		panel.ConsoleWrite("Attempting Twitch Connection...", 'blue')
	def GetNext(self):  # Get's the next PRIVMSG in the queue
		return self.GetNextOfType(MSG_CHAT)

	def GetNextOfType(self, msgType):
		if (self.dontQueue):
			print(
				"Trying to GetNextOfType() while dontQueue is equal to True. The queue will never get anything while it is True.")
			return
		while (len(self.messageQueue[msgType]) <= 0):
			pass  # Hang until a message is ready
		next = self.messageQueue[msgType][0]
		self.messageQueue[msgType].pop(0)
		return next

	def GetNextAny(self) -> Message:
		for key in self.messageQueue.keys():
			if (len(self.messageQueue[key]) > 0):
				next = self.messageQueue[key][0]
				self.messageQueue[key].pop(0)
				return next
		return None