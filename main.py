from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import framebuf,sys
import time
from psds1820 import get_temp
import dftds # TDS/ppm library
import network
import _thread
from mh_z19 import MH_Z19

#
# Pins
#
btnLeft = Pin(0, Pin.IN, Pin.PULL_DOWN)
btnOK = Pin(1, Pin.IN, Pin.PULL_DOWN)
btnRight = Pin(3, Pin.IN, Pin.PULL_DOWN)
ledRed = PWM(Pin(4))
ledYellow = Pin(5, Pin.OUT)
ledGreen = Pin(6, Pin.OUT)

ledRed.freq(8)

ledRed.duty_u16(0)
ledYellow.off()
ledGreen.off()

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
		"items": ["Temperatur", "Wasserqualitaet", "Panels", "Einstellungen", "Version", "Netzwerkausgang", "USB-Ausgang"], # type: ignore
		"focus": 0 # type: ignore
	},
	"save": { # type: ignore
		"items": ["Speichern", "Verwerfen"], # type: ignore
		"focus": 0 # type: ignore
	},
	"sensors": { # type: ignore
		"items": ["temp", "ppm", "co2", "exit"], # type: ignore
		"focus": 0 # type: ignore
	},
	"settings": { # type: ignore
		"items": ["ppm kalibrieren"], # type: ignore
		"focus": 0 # type: ignore
	},
	"aps": { # type: ignore
		"items": [], # type: ignore
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
# Networking
#
network.country("DE")
network.hostname("picoscratchmint")
nic = network.WLAN(network.STA_IF)

#
# Functions
#
def get_tds():
	try:
		tds_sensor = dftds.GravityTDS(28, adc_range=65535, k_value_repository=dftds.KValueRepositoryFlash("tds_calibration.json"))
		tds_sensor.begin()
		temp = get_temp()
		if temp == None:
			# tds_sensor.temperature = 25
			return None
		# else:
		tds_sensor.temperature = temp
		# tds_sensor.temperature = get_temp() # type: ignore
		tds_value = tds_sensor.update()
		return float('{0:.2g}'.format(tds_value))
	except:
		return None

def read_co2():
	sensor = MH_Z19(Pin(8), Pin(9), 1)
	return sensor.read_co2()

sensors = {
	"temp": { # type: ignore
		"read": get_temp, # type: ignore
		"unit": "*C", # type: ignore
		"min": -10, # type: ignore
		"max": 40, # type: ignore
		"friendlyName": "Temp.", # type: ignore
		"toolow": 10, # type: ignore
		"good": 20, # type: ignore
		"warn": 30, # type: ignore
		"bad": 40 # type: ignore
	},
	"ppm": { # type: ignore
		"read": get_tds, # type: ignore
		"unit": "ppm", # type: ignore
		"min": 0, # type: ignore
		"max": 500, # type: ignore
		"friendlyName": "ppm", # type: ignore
		"toolow": 70, # type: ignore
		"good": 80, # type: ignore
		"warn": 200, # type: ignore
		"bad": 400 # type: ignore
	}, # type: ignore
	"co2": { # type: ignore
		"read": read_co2, # type: ignore
		"unit": "ppm", # type: ignore
		"min": 300, # type: ignore ######################## TODO: change these values to sth better
		"max": 2200, # type: ignore
		"friendlyName": "CO2", # type: ignore
		"toolow": 0, # type: ignore
		"good": 400, # type: ignore
		"warn": 1300, # type: ignore
		"bad": 1700 # type: ignore
	}
}

def max4466():
	analog_value = ADC(28)
	conversion_factor =3.3/(65536)
	reading = analog_value.read_u16()*conversion_factor
	return reading

def trafficLight(value, goodlvl, warnlvl, badlvl, toolowlvl=0):
	on = 65535
	if value <= toolowlvl or value < goodlvl:
		ledRed.duty_u16(int(on/2)) # on
		ledYellow.off() # on
		ledGreen.off()
	elif value >= goodlvl and value < warnlvl:
		ledRed.duty_u16(0)
		ledYellow.off()
		ledGreen.on()
	elif value >= warnlvl and value < badlvl:
		ledRed.duty_u16(0)
		ledYellow.on()
		ledGreen.off()
	elif value >= badlvl:
		ledRed.duty_u16(on)
		ledYellow.off()
		ledGreen.off()

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
	time.sleep(btnSleep)
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

def gauge(v, maxv, x, y, w, h, minv=0):
	a = (v - minv) / (maxv - minv)
	a = a * w
	oled.rect(x, y, w, h, 1)
	oled.rect(x, y, int(a), h, 1, True)  # type: ignore

def startMenuItem(item):
	if item == 4: # Version
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
				gauge(temp, 40, 0, 30, 100, 30, -10)
				trafficLight(temp, sensors["temp"]["good"], sensors["temp"]["warn"], sensors["temp"]["bad"], sensors["temp"]["toolow"])
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
			filename = "t-" + str(currentTime[0]) + "-" + str(currentTime[1]) + "-" + str(currentTime[2]) + "-" + str(currentTime[3]) + "-" + str(currentTime[4]) + str(currentTime[5]) + ".csv"
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
	elif item == 1: # PPM
		while True:
			if btnOK.value():
				break
			oled.fill(0)
			oled.text("PPM Messung", 0, 0)
			tds_value = get_tds()
			if tds_value:
				oled.text(str(tds_value) + "ppm", 0, 15)
				gauge(tds_value, 500, 0, 30, 100, 30)
				trafficLight(tds_value, sensors["ppm"]["good"], sensors["ppm"]["warn"], sensors["ppm"]["bad"], sensors["ppm"]["toolow"])
			else:
				oled.text("Nicht verbunden", 0, 30)
			oled.show()
			time.sleep(0.3)
	elif item == 2: # panels
		while True:
			drawPanels()
			if not handlePanelButtons():
				break
	# elif item == 3: # settings
		# pass
		# sett = askQuestion("settings")
		# if sett == 0: # ppm calibration
			# oled.fill(0)
			# oled.text("ppm Kalibrierung", 0, 0)
			# oled.text("Bitte in 100ppm Wasser", 0, 15)
			# oled.text("Wasser tauchen", 0, 30)
			# oled.text("und OK druecken", 0, 45)
			# oled.show()
			# time.sleep(2)
			# while True:
			# 	if btnOK.value():
			# 		break
			# oled.fill(0)
			# oled.text("Kalibriere...", 0, 0)
			# oled.show()
			# tds_sensor = dftds.GravityTDS(28, adc_range=65535, k_value_repository=dftds.KValueRepositoryFlash("tds_calibration.json"))
			# tds_sensor.temperature = get_temp() # type: ignore
			# tds_sensor.begin()
			# tds_sensor.update()
			# tds_sensor.calibrate(100)
			# oled.fill(0)
			# oled.text("Kalibriert", 0, 0)
			# oled.show()
			# time.sleep(2)
	elif item == 5: # networking
		# oled.fill(0)
		# oled.text("Scanning...", 0, 0)
		# oled.show()
		# nic.active(True)
		# aps = nic.scan()
		# print(len(aps))
		# menus["aps"]["items"] = []
		# menus["aps"]["focus"] = 0
		# for ap in aps:
		# 	menus["aps"]["items"].append(ap[0].decode("utf-8") + " " + str(ap[3]) + "dBm")
		# ap = askQuestion("aps")
		# ap = menus["aps"]["items"][ap]
		# ap = ap.split(" ")
		# ap.pop()
		# ap = " ".join(ap)
		# oled.fill(0)
		# oled.text("Connecting...", 0, 0)
		# oled.show()
		# nic.connect(ap, "88888888")
		# import config
		# oled.fill(0)
		# oled.text("Connecting...", 0, 0)
		# oled.show()
		# nic.active(True)
		# time.sleep(1)
		# print(config.ssid, config.password)
		# nic.connect(ssid=config.ssid, key=config.password)
		# while nic.status() == network.STAT_CONNECTING:
		# 	pass
		# oled.fill(0)
		# if nic.status() == network.STAT_GOT_IP:
		# 	ip = nic.ifconfig()[0]
		# 	oled.text("Connected", 0, 0)
		# 	oled.text(ip, 0, 15)
		# elif nic.status() == network.STAT_WRONG_PASSWORD:
		# 	oled.text("Wrong password", 0, 0)
		# elif nic.status() == network.STAT_NO_AP_FOUND:
		# 	oled.text("No AP found", 0, 0)
		# elif nic.status() == network.STAT_CONNECT_FAIL:
		# 	oled.text("Connection failed", 0, 0)
		# print(nic.status())
		# oled.show()
		# time.sleep(3)
		networkOutput()
	elif item == 6: # enable serial
		# _thread.start_new_thread(serialThread, ())
		# remove the menu item
		# menus["main"]["items"].pop(6)
		# menus["main"]["focus"] = 0
		serialThread()
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

def invertArea(x, y, w, h):
	for i in range(w):
		for j in range(h):
			oled.pixel(x+i, y+j, not oled.pixel(x+i, y+j))

panels = ["temp", "co2", "add"]
selectedPanel = 0
panelheight = 30

def drawPanels():
	oled.fill(0)
	for i, panel in enumerate(panels):
		h = i*panelheight + 2
		# if i > 0:
		# 	h = h + 3
		# scroll the height away depending on the selected panel
		h = h - (selectedPanel * panelheight)
		if selectedPanel % 2 != 0:
			h = h + panelheight
		
		oled.rect(0, h, display_width, panelheight, 1)

		if panel == "add":
			oled.text("Neuer Sensor...", 5, 5+h, 1)
		else:
			value = 0
			unit = ""
			min = 0
			max = 0
			friendlyName = panel
			if panel in sensors:
				value = sensors[panel]["read"]()
				unit = sensors[panel]["unit"]
				min = sensors[panel]["min"]
				max = sensors[panel]["max"]
				friendlyName = sensors[panel]["friendlyName"] if "friendlyName" in sensors[panel] else panel
				if i == selectedPanel:
					if value == None:
						ledRed.duty_u16(0)
						ledYellow.off()
						ledGreen.off()
					else:
						trafficLight(value, sensors[panel]["good"], sensors[panel]["warn"], sensors[panel]["bad"], sensors[panel]["toolow"])
			
			oled.text(friendlyName, 5, 5+h, 1)

			if value == None:
				oled.text("Nicht verbunden", 5, 5+h+10, 1)
			else:
				text = str(value) + unit
				# right aligned, every char is 8px wide
				oled.text(text, display_width - (len(text) * 8) - 5, 5+h, 1)

				gauge(value, max, 5, 5+h+10, display_width - 10, 10, min)
		if i == selectedPanel:
			invertArea(0, h, display_width, panelheight)
	oled.show()

def handlePanelButtons():
	global selectedPanel
	if btnLeft.value():
		selectedPanel = selectedPanel - 1
		if selectedPanel < 0:
			selectedPanel = len(panels) - 1
		drawPanels()
		time.sleep(btnSleep)
	elif btnRight.value():
		selectedPanel = selectedPanel + 1
		if selectedPanel > len(panels) - 1:
			selectedPanel = 0
		drawPanels()
		time.sleep(btnSleep)
	elif btnOK.value():
		if panels[selectedPanel] == "add":
			sensor = menus["sensors"]["items"][askQuestion("sensors")]
			if sensor == "exit":
				return False
			panels.insert(len(panels) - 1, sensor)
		else:
			panels.pop(selectedPanel)
		drawPanels()
		time.sleep(btnSleep)
	return True

#
# Serial Thread
#
def serialThread():
	last_temp = -1
	last_ppm = -1
	oled.fill(0)
	oled.text("Daten ueber USB", 0, 0, 1)
	oled.text("OK zum beenden", 0, 10, 1)
	oled.show()
	time.sleep(1)
	# this threads job is printing json data to the serial port, all sensors are polled here
	while True:
		try:
			temp = get_temp()
			last_temp = temp
		except:
			temp = last_temp
		try:
			tds_value = get_tds()
			last_ppm = tds_value
		except:
			tds_value = last_ppm
		print("{\"temp\":" + str(temp) + ",\"ppm\":" + str(tds_value) + "}")
		if btnOK.value():
			break
		time.sleep(1)

def networkOutput():
	pass

# _thread.start_new_thread(serialThread, ())

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