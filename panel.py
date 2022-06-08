from tkinter import *
import datetime, random

MAX_LINES = 500.0
BOLD_TIMESTAMP = False


root = None
consoleLog = None
consoleInput = None
queuedCommands = []

def TestMessageCommand():
	ConsoleWrite("Test Message",'blue')

def GetNextCommand():
	if(len(queuedCommands) == 0): return None;
	c = queuedCommands[0]
	queuedCommands.pop(0)
	return c

def GenerateTimeStamp():
	return "["+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")+"] "

def ConsoleWrite(text,color='white',boldPrefixChars=0):
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

	consoleLog.config(state='disabled')

def ConsoleInputEvent(*args):
	commandString = consoleInput.get("1.0","end-1c").strip()
	timeStamp = GenerateTimeStamp()
	newText = timeStamp + commandString
	if(BOLD_TIMESTAMP):
		ConsoleWrite(newText,color='red',boldPrefixChars=len(timeStamp))
	else:
		ConsoleWrite(newText, color='red', boldPrefixChars=0)
	consoleInput.delete('1.0','end')
	queuedCommands.append(commandString.split(" "))

def CreatePanel():
	global root, consoleLog, consoleInput
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

	settingsLabel = Label(root,text="Settings",font=("Arial",25))
	settingsLabel.grid(row=0,column=1,sticky="NE")
	settingsLabel.grid_anchor("n")

	consoleTestSettingButton = Button(root,text="Test Message",command=TestMessageCommand)
	consoleTestSettingButton.grid(row=0,column=1)

def Tick():
	global root
	root.update_idletasks()
	root.update()

if __name__ == '__main__':
	CreatePanel()
	while True:
		Tick()
