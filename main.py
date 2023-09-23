from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import framebuf,sys
import time
from psds1820 import get_temp

#
# Pins
#
btnLeft = Pin(0, Pin.IN, Pin.PULL_DOWN)
btnOK = Pin(1, Pin.IN, Pin.PULL_DOWN)
btnRight = Pin(3, Pin.IN, Pin.PULL_DOWN)

#
# Constants
#
display_width = 128 # SSD1306 width
display_height = 64   # SSD1306 height
picoscratch_logo = bytearray(b'BM>\x02\x00\x00\x00\x00\x00\x00>\x00\x00\x00(\x00\x00\x00@\x00\x00\x00@\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x02\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xfc\x00\x00\x00\x00\x00\x0f\xff\xff\x80\x00\x00\x00\x00\x1f\xff\xff\xe0\x00\x00\x00\x00?\x00\x0f\xf0\x00\x00\x00\x00|\x00\x01\xf8\x00\x00\x00\x00x\x00\x00|\x00\x00\x00\x00\xf0\x00\x00>\x00\x00\x00\x00\xe0\x00\x00\x1e\x00\x00\x00\x00\xe0\xff\xf8\x0e\x00\x00\x00\x00\xe0\x0c\x0e\x0f\x00\x00\x00\x00\xe0\x0c\x03\x0f\x00\x00\x00\x00\xf0\x0c\x03\x07\x00\x00\x00\x00x\x04\x01\x07\x00\x00\x00\x00|\x04\x01\x07\x00\x00\x00\x00?\x04\x02\x0f\x00\x00\x00\x00\x1f\x04\x06\x0f\x00\x00\x00\x00\x0f\x04x\x1e\x00\x00\x00\x00\x07\x07\x80\x1e\x00\x00\x00\x00\x07\x04\x00<\x00\x00\x00\x00\x07\x04\x00|\x00\x00\x00\x00\x07\x04\x01\xf8\x00\x00\x00\x00\x07\x04\x0f\xf0\x00\x00\x00\x00\x0f\x04\x1f\xe0\x00\x00\x00\x00\x1f\x04\x1f\xc0\x00\x00\x00\x00?\x04\x03\xe0\x00\x00\x00\x00|\x04\x01\xe0\x00\x00\x00\x00x\x04\x00\xe0\x00\x00\x00\x00p\x04\x00\xe0\x00\x00\x00\x00\xf0\x07\xf0\xe0\x00\x00\x00\x00\xf0\xff\xe0\xe0\x00\x00\x00\x00\xf0\x00\x00\xe0\x00\x00\x00\x00\xf0\x00\x01\xe0\x00\x00\x00\x00x\x00\x03\xe0\x00\x00\x00\x00x\x00\x07\xc0\x00\x00\x00\x00>\x07\xff\xc0\x00\x00\x00\x00\x1f\xff\xff\x80\x00\x00\x00\x00\x0f\xff\xfe\x00\x00\x00\x00\x00\x03\xff\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
lineskip = 15
btnSleep = 0.3

menuShift = 0
maxItems = 4
# Menus
menus = {
	"main": { # type: ignore
		"items": ["Temperatur", "pH-Wert", "World", "Version", "Credits"], # type: ignore
		"focus": 0 # type: ignore
	},
	"save": { # type: ignore
		"items": ["Speichern", "Verwerfen"], # type: ignore
		"focus": 0 # type: ignore
	}
}
currentMenu = "main"
isInMenu = False
# mainMenuItems = ["Temperatur", "pH-Wert", "World", "Version", "Credits"]
# mainMenuFocus = 0

#
# Display
#
# 0x3C i2c address usually, can also rarely be 0x3D
screen_i2c = I2C(1,scl=Pin(27),sda=Pin(26))  # start I2C on I2C1 (GPIO 26/27)
# i2c_addr = [hex(ii) for ii in screen_i2c.scan()] # get I2C address in hex format
# if i2c_addr==[]:
# 	print('No I2C Display Found') 
# 	sys.exit() # exit routine if no dev found
# else:
# 	print("I2C Address      : {}".format(i2c_addr[0])) # I2C device address
# 	print("I2C Configuration: {}".format(screen_i2c)) # print I2C params

oled = SSD1306_I2C(display_width, display_height, screen_i2c) # oled controller

#
# Functions
#
def drawLogo(logo):
	fb = framebuf.FrameBuffer(logo, 64, 64, framebuf.MONO_HLSB)

	oled.fill(0)
	oled.blit(fb, 0, -10)

	start_x = 40
	start_y = 12
	txt_array = ["PicoScratch", "MINT", "Koffer"]
	for iter_ii,txt in enumerate(txt_array):
		oled.text(txt, start_x, start_y+(iter_ii*lineskip))
	
	oled.show()

def askQuestion(men):
	switchMenu(men)
	while True:
		if btnOK.value():
			break
		checkButtons()
	return menus[currentMenu]["focus"]

def drawMenu():
	lineskip = 15
	oled.fill(0)
	items = menus[currentMenu]["items"]
	focusedMenuItem = menus[currentMenu]["focus"]
	for i, txt in enumerate(items):
		oled.rect(0, i*lineskip-menuShift, display_width, lineskip, 1 if focusedMenuItem == i else 0, True) # type: ignore
		oled.text(txt, 5, 5+(i*lineskip)-menuShift, 0 if focusedMenuItem == i else 1)
	oled.show()

def gauge(v, maxv, x, y, w, h):
	a = v / maxv
	a = a * w
	oled.rect(x, y, w, h, 1)
	oled.rect(x, y, int(a), h, 1, True) # type: ignore

def startMenuItem(item):
	if item == 3: # Version
		oled.fill(0)
		oled.text("PicoScratch", 0, 0)
		oled.text("MINT Koffer", 0, 15)
		oled.text("UI Version 0.1", 0, 30)
		oled.text("HW Version PROTO", 0, 45)
		oled.show()
		while True:
			if btnOK.value():
				break
	elif item == 0: # Temp
		data = ["Zeit,Temperatur"]
		count = 0
		while True:
			if btnOK.value():
				time.sleep(0.3)
				break
			oled.fill(0)
			oled.text("Temperatursensor", 0, 0)
			temp = get_temp()
			count += 1
			if count % 3 == 0: # with 0.3s sleep, this is every second
				currentTime = time.localtime() # touple: (year, month, day, hour, minute, second, weekday, yearday)
				data.append(str(currentTime[3]) + ":" + str(currentTime[4]) + str(currentTime[5]) + "," + str(temp))
			if temp:
				oled.text(str(temp) + "*C", 0, 15)
				gauge(temp, 40, 0, 30, 100, 30)
			else:
				oled.text("Nicht verbunden", 0, 30)
			oled.show()
			time.sleep(0.3)
		shouldSave = askQuestion("save")
		if shouldSave == 0:
			oled.fill(0)
			oled.text("Speichern...", 0, 0)
			oled.show()
			currentTime = time.localtime() # touple: (year, month, day, hour, minute, second, weekday, yearday)
			filename = "results-" + str(currentTime[0]) + "-" + str(currentTime[1]) + "-" + str(currentTime[2]) + "-" + str(currentTime[3]) + "-" + str(currentTime[4]) + str(currentTime[5]) + ".csv"
			with open(filename, "w") as f:
				for line in data:
					f.write(line + "\n")
				f.close()
			oled.fill(0)
			oled.text("Gespeichert unter", 0, 0)
			oled.text(filename, 0, 15)
			oled.show()
			time.sleep(2)
		else:
			oled.fill(0)
			oled.text("Verworfen", 0, 0)
			oled.show()
			time.sleep(2)
	elif item == 1: # pH
		while True:
			if btnOK.value():
				break
			oled.fill(0)
			oled.text("pH-Wert Messung", 0, 0)
			pH = 0
			oled.text(str(pH), 0, 15)
			gauge(pH, 40, 0, 30, 100, 30)
			oled.show()
			time.sleep(0.3)
	else: # Not implemented
		oled.fill(0)
		oled.text("Not Implemented", 0, 0)
		oled.show()
		time.sleep(3)
	oled.fill(0)
	oled.show()
	time.sleep(1.5)

def calculateShift():
	global menuShift
	menuShift = int(menus[currentMenu]["focus"] / maxItems) * (lineskip * maxItems)

def switchMenu(to):
	global currentMenu
	currentMenu = to
	calculateShift()
	drawMenu()

#
# Main
#
drawLogo(picoscratch_logo)

# Wait for OK button
while True:
	v = btnOK.value()
	if v:
		break

drawMenu()

time.sleep(btnSleep)

def checkButtons():
	global isInMenu, menuShift, menus
	isAnyButtonPressed = btnLeft.value() or btnOK.value() or btnRight.value()
	navigationButton = "up" if btnLeft.value() else "down" if btnRight.value() else None
	items = menus[currentMenu]["items"]
	if navigationButton: # up or down
		# Change the focused menu item
		menus[currentMenu]["focus"] = menus[currentMenu]["focus"] + (-1 if navigationButton == "up" else 1)
		# Wrap around if needed
		if menus[currentMenu]["focus"] < 0:
			menus[currentMenu]["focus"] = len(items) - 1
		elif menus[currentMenu]["focus"] > len(items) - 1:
			menus[currentMenu]["focus"] = 0
		# Shift the menu if needed
		calculateShift()
		time.sleep(btnSleep)
		drawMenu()
	elif btnOK.value(): # select
		if currentMenu != "main":
			return
		time.sleep(btnSleep)
		startMenuItem(menus[currentMenu]["focus"])
		time.sleep(btnSleep)
		switchMenu("main")
		# drawMenu()

while True:
	checkButtons()