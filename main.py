from display import drawLogo, oled, display_width, display_height, readPBM, brightness
drawLogo(readPBM("logo.pbm"), ["PicoScratch", "Loading..."])
from machine import Pin, I2C, ADC, PWM
import framebuf,sys
import time
from psds1820 import get_temp
import dftds # TDS/ppm library
import network
import _thread
from mh_z19 import MH_Z19
import config
import uota
import machine
import json
import select
import os
from panels import drawPanels, handlePanelButtons
from sensor import sensors
from util import get_serial, powerSave
import gc

#
# Pins
#
btnLeft = Pin(0, Pin.IN, Pin.PULL_DOWN)
btnOK = Pin(1, Pin.IN, Pin.PULL_DOWN)
btnRight = Pin(3, Pin.IN, Pin.PULL_DOWN)
btnBack = Pin(7, Pin.IN, Pin.PULL_DOWN)
ledRed = PWM(Pin(4))
ledYellow = Pin(5, Pin.OUT)
ledGreen = Pin(6, Pin.OUT)

ledRed.freq(8)

ledRed.duty_u16(0)
ledYellow.off()
ledGreen.off()

#
# Sensor I2C Bus
#
i2c = I2C(0, sda=Pin(8), scl=Pin(9))

#
# Constants
#
lineskip = 15
btnSleep = 0.3

menuShift = 0
maxItems = 4
# Menus
menus = {
	"main": { # type: ignore
		"items": ["Panels", "Einstellungen", "Test", "Skripte", "Version", "Netzwerkausgang", "USB-Ausgang"], # type: ignore
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
		"items": ["X Energiesparen", "Helligkeit: 100"], # type: ignore
		"focus": 0 # type: ignore
	},
	"aps": { # type: ignore
		"items": [], # type: ignore
		"focus": 0 # type: ignore
	},
	"scripts": {
		"items": [], # type: ignore
		"focus": 0 # type: ignore
	}
}
currentMenu = "main"
isInMenu = False
# mainMenuItems = ["Temperatur", "pH-Wert", "World", "Version", "Credits"]
# mainMenuFocus = 0

secretCount = 0

#
# Networking
#
network.country("DE")
network.hostname("picoscratchmint")
nic = network.WLAN(network.STA_IF)
version = "-1"
with open('version', 'r') as f:
	version = f.read().strip()

#
# Functions
#
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

def askQuestion(men):
	switchMenu(men)
	time.sleep(btnSleep)
	while True:
		if btnOK.value():
			break
		if btnBack.value():
			return -1
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
		oled.text(get_serial(), 0, 15)
		oled.text("UI Version " + version, 0, 30)
		oled.text("HW Version rev1", 0, 45)
		oled.show()
		while True:
			if btnOK.value():
				break
	#elif item == 0: # Temp
	#	data = ["Zeit,Temperatur"]
	#	count = 0
	#	while True:
	#		if btnOK.value():
	#			time.sleep(0.3)
	#			break
	#		oled.fill(0)
	#		oled.text("Temperatursensor", 0, 0)
	#		temp = get_temp()
	#		count += 1
	#		if count % 3 == 0: # with 0.3s sleep, this is every second
	#			currentTime = time.localtime() # touple: (year, month, day, hour, minute, second, weekday, yearday)
	#			data.append(str(currentTime[3]) + ":" + str(currentTime[4]) + str(currentTime[5]) + "," + str(temp))
	#		if temp:
	#			oled.text(str(temp) + "*C", 0, 15)
	#			gauge(temp, 40, 0, 30, 100, 30, -10)
	#			trafficLight(temp, sensors["temp"]["good"], sensors["temp"]["warn"], sensors["temp"]["bad"], sensors["temp"]["toolow"])
	#		else:
	#			oled.text("Nicht verbunden", 0, 30)
	#		oled.show()
	#		time.sleep(0.3)
	#	shouldSave = askQuestion("save")
	#	if shouldSave == 0:
	#		oled.fill(0)
	#		oled.text("Speichern...", 0, 0)
	#		oled.show()
	#		currentTime = time.localtime() # touple: (year, month, day, hour, minute, second, weekday, yearday)
	#		filename = "t-" + str(currentTime[0]) + "-" + str(currentTime[1]) + "-" + str(currentTime[2]) + "-" + str(currentTime[3]) + "-" + str(currentTime[4]) + str(currentTime[5]) + ".csv"
	#		with open(filename, "w") as f:
	#			for line in data:
	#				f.write(line + "\n")
	#			f.close()
	#		oled.fill(0)
	#		oled.text("Gespeichert unter", 0, 0)
	#		oled.text(filename, 0, 15)
	#		oled.show()
	#		time.sleep(2)
	#	else:
	#		oled.fill(0)
	#		oled.text("Verworfen", 0, 0)
	#		oled.show()
	#		time.sleep(2)
	#elif item == 1: # PPM
	#	while True:
	#		if btnOK.value():
	#			break
	#		oled.fill(0)
	#		oled.text("PPM Messung", 0, 0)
	#		tds_value = get_tds()
	#		if tds_value:
	#			oled.text(str(tds_value) + "ppm", 0, 15)
	#			gauge(tds_value, 500, 0, 30, 100, 30)
	#			trafficLight(tds_value, sensors["ppm"]["good"], sensors["ppm"]["warn"], sensors["ppm"]["bad"], sensors["ppm"]["toolow"])
	#		else:
	#			oled.text("Nicht verbunden", 0, 30)
	#		oled.show()
	#		time.sleep(0.3)
	elif item == 0: # panels
		while True:
			drawPanels(oled, sensors, i2c, ledRed, ledYellow, ledGreen, display_width, display_height)
			if not handlePanelButtons(btnLeft, btnOK, btnRight, btnBack):
				break
	elif item == 1: # settings
		while True:
			menus["settings"]["items"][0] = ("X" if powerSave() else "-") + " Energiesparen"
			menus["settings"]["items"][1] = "Helligkeit " + str(int((brightness() / 255) * 100)) + "%"
			option = askQuestion("settings")
			if option == -1:
				break
			elif option == 0: # energy saver
				powerSave(not powerSave())
			elif option == 1:
				current = (brightness() / 255) * 100
				current = current - 20
				if current < 0:
					current = 100
				brightness(int((current / 100) * 255))
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
		ledGreen.on()
		oled.fill(0)
		# oled.text("Scanning...", 0, 0)
		oled.blit(readPBM("scanningnets.pbm"), 0, 0)
		oled.show()
		nic.active(True)
		aps = nic.scan()
		found = None
		for ap in aps:
			print(ap[0])
			for net in config.networks:
				if net["ssid"] == ap[0].decode("utf-8"):
					found = net
					break
			if found:
				break
		ledGreen.off()
		if found == None:
			ledRed.duty_u16(255*255)
			oled.fill(0)
			oled.text("No AP found", 0, 0)
			oled.show()
			nic.active(False)
			time.sleep(1)
			ledRed.duty_u16(0)
			return
		oled.fill(0)
		# oled.text("Connecting...", 0, 0)
		oled.blit(readPBM("connectingnet.pbm"), 0, 0)
		oled.show()
		nic.connect(found["ssid"], found["password"])
		while not nic.isconnected():
			ledYellow.on()
			time.sleep(0.5)
			ledYellow.off()
			time.sleep(0.5)
		oled.fill(0)
		# oled.text("Checking for", 0, 0)
		# oled.text("updates...", 0, 10)
		oled.blit(readPBM("searchingupdates.pbm"), 0, 0)
		oled.show()
		checkForUpdates()
		from packetjob import networkOutput
		try:
			networkOutput(btnOK, nic)
		except Exception as e:
			print(e)
	elif item == 6: # enable serial
		# _thread.start_new_thread(serialThread, ())
		# remove the menu item
		# menus["main"]["items"].pop(6)
		# menus["main"]["focus"] = 0
		from packetjob import serialThread
		serialThread(btnOK, nic)
	elif item == 2: # test
		import test
	elif item == 3: # scripts
		files = os.listdir("/user")
		menus["scripts"]["items"] = []
		menus["scripts"]["focus"] = 0
		for file in files:
			if not file.endswith(".py"):
				continue
			menus["scripts"]["items"].append(file.replace(".py", ""))
		script = askQuestion("scripts")
		if not script == -1:
			print("Running script from /user/" + menus["scripts"]["items"][script] + ".py")
			exec(open("/user/" + menus["scripts"]["items"][script] + ".py").read())
	else: # Not implemented
		oled.fill(0)
		oled.text("Not Implemented", 0, 0)
		oled.show()
		time.sleep(3)
	ledRed.duty_u16(0)
	ledGreen.off()
	ledYellow.off()
	oled.fill(0)
	oled.show()
	gc.collect()
	time.sleep(1.5)

def calculateShift():
	global menuShift
	menuShift = int(menus[currentMenu]["focus"] / maxItems) * (lineskip * maxItems)

def switchMenu(to):
	global currentMenu
	currentMenu = to
	calculateShift()
	drawMenu()

def checkForUpdates():
	ledRed.duty_u16(int(65535/2))
	if uota.check_for_updates(quiet=False):
		oled.fill(0)
		oled.text("Updating", 0, 0)
		oled.text("firmware...", 0, 10)
		oled.text("DO NOT POWER OFF", 0, 20)
		oled.show()
		uota.install_new_firmware()
		ledRed.duty_u16(0)
		machine.reset()
	ledRed.duty_u16(0)

#
# Main
#
# drawLogo(picoscratch_logo, ["PicoScratch", "Press OK"])

# Wait for OK button
# while True:
# 	v = btnOK.value()
# 	if v:
# 		break

drawMenu()

time.sleep(btnSleep)

def checkButtons():
	global isInMenu, menuShift, menus, secretCount
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
	elif btnBack.value(): # secret
		secretCount = secretCount + 1
		print(secretCount)
		if secretCount == 10:
			oled.fill(0)
			oled.text("BOO!", 0, 0)
			oled.show()
			time.sleep(3)
			drawMenu()
		time.sleep(btnSleep)

while True:
	checkButtons()