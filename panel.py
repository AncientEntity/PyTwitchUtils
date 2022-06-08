from tkinter import *
import datetime, random, json, os.path

MAX_LINES = 500.0
BOLD_TIMESTAMP = False


root = None
consoleLog = None
consoleInput = None
settingsFrame = None

configRoot = None
configSettings = {}
configSettingsInputs = []

settingsButtons = []
queuedCommands = []
consoleLogQueue = []

def TestMessageCommand():
	ConsoleWrite("Test Message",'blue')

def GetNextCommand():
	if(len(queuedCommands) == 0): return None;
	c = queuedCommands[0].split(" ")
	queuedCommands.pop(0)
	return c
def GetNextCommandRaw():
	if(len(queuedCommands) == 0): return None;
	c = queuedCommands[0]
	queuedCommands.pop(0)
	return c

def GenerateTimeStamp():
	return "["+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")+"] "

def ConsoleWrite(text,color='black',boldPrefixChars=0):
	consoleLogQueue.append([text,color,boldPrefixChars])

def _ConsoleWrite(text,color='black',boldPrefixChars=0):
	consoleLog.config(state='normal')
	firstIndex = float(consoleLog.index("end"))
	consoleLog.insert('end', text+'\n')
	lastIndex = float(consoleLog.index("end"))
	#print(firstIndex," ",lastIndex)
	randomSuffix = str(random.randint(-99999999,9999999))
	consoleLog.tag_add("color"+randomSuffix,firstIndex-1,lastIndex-1)
	consoleLog.tag_config("color"+randomSuffix,background='white',foreground=color)

	if(boldPrefixChars > 0):
		print(firstIndex-1,str(firstIndex)+"-"+str(boldPrefixChars)+"c")
		consoleLog.tag_add("bold"+randomSuffix,firstIndex-1,str(firstIndex-1)+"+"+str(boldPrefixChars)+"c")
		consoleLog.tag_config("bold"+randomSuffix,font=('bold'))

	while lastIndex > MAX_LINES:
		print("Deleting")
		consoleLog.delete("1.0")
		lastIndex = float(consoleLog.index("end"))

	consoleLog.see("end")
	consoleLog.config(state='disabled')

def ConsoleInputEvent(*args):
	commandString = consoleInput.get("1.0","end-1c").strip()
	timeStamp = GenerateTimeStamp()
	newText = timeStamp + commandString
	if(BOLD_TIMESTAMP):
		ConsoleWrite(newText,color='grey',boldPrefixChars=len(timeStamp))
	else:
		ConsoleWrite(newText, color='grey', boldPrefixChars=0)
	consoleInput.delete('1.0','end')
	queuedCommands.append(commandString)

def SetConfigSetting(settingName,curValue):
	configSettings[settingName] = curValue
def GetConfigSetting(settingName):
	return configSettings[settingName]

def GetButtonByIndex(i) -> Button:
	return settingsButtons[i]


def CreateNewSettingsButton(text,func):
	"""Returns the index of the button created."""
	global settingsButtons, settingsFrame
	newButton = Button(settingsFrame,text=text,command=func)
	newButton.grid(row=len(settingsButtons)+1,column=0)
	settingsButtons.append(newButton)
	return len(settingsButtons) - 1 #Return index of button

def ReadConfigFile():
	if(os.path.exists("config.dat")):
		f = open("config.dat","r+")
		d : dict = json.loads(f.read())
		for item in d.items():
			configSettings[item[0]] = item[1]
		f.close()
	else:
		WriteConfigFile()

def WriteConfigFile():
	global configSettingsInputs,configSettings
	i = 0
	for settingName in configSettings.keys():
		configSettings[settingName] = configSettingsInputs[i].get("1.0","end").strip()

		i += 1

	f = open("config.dat", "w+")
	f.write(json.dumps(configSettings))
	f.close()

def CreateConfig():
	global configRoot, configSettingsInputs
	ReadConfigFile()
	configRoot = Tk()
	configRoot.title("Config")
	configRoot.geometry("450x400")
	i = 0
	configSettingsInputs = []
	for config in configSettings.items():
		l = Label(configRoot,text=config[0])
		l.grid(row=i,column=0)

		input = Text(configRoot,width=40,height=1)
		input.insert(0.0,configSettings[config[0]])
		input.grid(row=i,column=1)
		configSettingsInputs.append(input)
		i += 1
	configSaveButton = Button(configRoot,text="Save",command=WriteConfigFile)
	configSaveButton.grid(row=i,column=0,pady=20)


def CreatePanel():
	global root, consoleLog, consoleInput, settingsFrame
	root = Tk()
	root.title("Control Panel")
	root.geometry("875x390")
	consoleLog = Text(root,width = 80,height = 20)
	consoleLog.config(state='disabled')
	consoleLog.grid(row=0,padx=10,pady=10)

	#consoleLog.pack()
	consoleInput = Text(root,width = 80, height = 1 )
	consoleInput.bind("<Return>",ConsoleInputEvent)
	consoleInput.grid(row=1)

	settingsFrame = Frame()
	settingsFrame.grid(row=0,column=1)

	settingsLabel = Label(settingsFrame,text="Settings",font=("Arial",25))
	settingsLabel.grid(row=0,column=0,sticky="NE")
	settingsLabel.grid_anchor("n")

	#CreateNewSettingsButton("Test Message",TestMessageCommand)
	CreateNewSettingsButton("Open Config",CreateConfig)

	ConsoleWrite(GenerateTimeStamp()+"Panel Setup Complete",'black')

def Tick():
	global root, configRoot
	while (len(consoleLogQueue) > 0):
		cur = consoleLogQueue[0]
		_ConsoleWrite(cur[0], cur[1], cur[2])
		consoleLogQueue.pop(0)
	if root != None:
		root.update_idletasks()
		root.update()
	if configRoot != None:
		try:
			configRoot.update_idletasks()
			configRoot.update()
		except:
			configRoot = None #configRoot was x'ed out of. So set it to None.

ReadConfigFile()

if __name__ == '__main__':
	CreatePanel()
	while True:
		Tick()
