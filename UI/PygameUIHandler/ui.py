import pygame, threading, time

class Window:
	window : pygame.Surface = None
	def __init__(self,width : int,height : int,caption : str="Unnamed Window"):
		self.isActive = False
		self.width = width
		self.height = height
		self.caption = caption
		self.screen = None
		self.background = [255,255,255]
		self.handlerThread = None
		self.elements : list[Element] = []
	def Init(self):
		if(pygame.display.get_init() == False):
			pygame.init()
		pygame.display.set_caption(self.caption)
		self.screen = pygame.display.set_mode((self.width,self.height))
		Window.window = self.screen
		self.isActive = True
		self.handlerThread = threading.Thread(target=self.HandlerThread,args=())
		for element in self.elements:
			element.Start()
		self.handlerThread.start()
	def IsActive(self):
		return self.isActive
	def SetIcon(self,surface):
		pygame.display.set_icon(surface)
	def HandlerThread(self):
		print("Window Handler("+self.caption+") has started")
		lastTime = time.time()
		delta = 0
		while self.isActive:
			self.screen.fill(self.background)

			inputs = []#pygame.key.get_pressed()

			for element in self.elements:
				element.Update(inputs)

			pygame.display.update()

			delta = time.time() - lastTime
			lastTime = time.time()
			time.sleep(1.0 / 60.0)
		print("Window Handler("+self.caption+") has ended")
	def AddElement(self,element,name=None):
		if(name != None):
			element.name = name
		self.elements.append(element)


class Element:
	def __init__(self,name : str,position : tuple,size : tuple):
		self.name = name
		self.position = position
		self.size = size
	def Start(self):
		pass
	def Update(self,inputs):
		pass

class Panel(Element):
	def __init__(self,name,position,size,color):
		super().__init__(name,position,size)
		self.color = color
	def Update(self,inputs):
		pygame.draw.rect(Window.window,self.color,[self.position[0],self.position[1],self.size[0],self.size[1]])

class Image(Element):
	def __init__(self,name,position,size,sprite : str):
		super().__init__(name,position,size)
		self.spriteFile = sprite
		self.sprite = None
	def Start(self):
		self.sprite = pygame.image.load(self.spriteFile)
		self.sprite = pygame.transform.scale(self.sprite,(int(self.size[0] * self.sprite.get_width()),int(self.size[1] * self.sprite.get_height())))
	def Update(self,inputs):
		Window.window.blit(self.sprite,self.position)

if __name__ == '__main__':
	w = Window(500,500,"PP")
	p = Panel("Joe Mama",[10,50],[50,150],[158,0,234])
	p2 = Panel("Yee",[10,10],[50,150],[255,0,0])
	p3 = Panel("Joe Mama",[150,10],[100,150],[23,0,244])
	img1 = Image("Bold & Brash",[10,50],[0.5,0.2],"Sample\\boldandbrash.png")
	w.elements.append(p)
	w.elements.append(p2)
	w.elements.append(p3)
	w.elements.append(img1)
	w.Init()