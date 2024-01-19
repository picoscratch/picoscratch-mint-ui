from display import drawLogo, oled, display_width, display_height, picoscratch_logo
drawLogo(picoscratch_logo, ["PicoScratch", "Loading..."])
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
import psscd4x
from panels import drawPanels, handlePanelButtons

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
		"items": ["ppm kalibrieren"], # type: ignore
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
	#"co2": { # type: ignore
	#	"read": read_co2, # type: ignore
	#	"unit": "ppm", # type: ignore
	#	"min": 300, # type: ignore ######################## TODO: change these values to sth better
	#	"max": 2200, # type: ignore
	#	"friendlyName": "CO2", # type: ignore
	#	"toolow": 0, # type: ignore
	#	"good": 400, # type: ignore
	#	"warn": 1300, # type: ignore
	#	"bad": 1700 # type: ignore
	#},
	"co2": { # type: ignore
		"isI2C": True, # type: ignore
		"addr": psscd4x.I2C_ADDR, # type: ignore
		"read": psscd4x.read_i2c_co2, # type: ignore
		"init": psscd4x.driver_init, # type: ignore
		"unit": "ppm", # type: ignore
		"min": 100, # type: ignore
		"max": 2000, # type: ignore
		"friendlyName": "CO2", # type: ignore
		"toolow": -1, # type: ignore
		"good": 800, # type: ignore
		"bad": 1200 # type: ignore
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

def get_serial():
	uid = machine.unique_id()
	serial_number = ''.join(['{:02X}'.format(byte) for byte in uid])
	return serial_number

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
			if not handlePanelButtons(btnLeft, btnOK, btnRight):
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
		ledGreen.on()
		oled.fill(0)
		oled.text("Scanning...", 0, 0)
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
			ledRed.on()
			oled.fill(0)
			oled.text("No AP found", 0, 0)
			oled.show()
			nic.active(False)
			time.sleep(1)
			ledRed.off()
			return
		oled.fill(0)
		oled.text("Connecting...", 0, 0)
		oled.show()
		nic.connect(found["ssid"], found["password"])
		while not nic.isconnected():
			ledYellow.on()
			time.sleep(0.5)
			ledYellow.off()
			time.sleep(0.5)
		oled.fill(0)
		oled.text("Checking for", 0, 0)
		oled.text("updates...", 0, 10)
		oled.show()
		checkForUpdates()
	elif item == 6: # enable serial
		# _thread.start_new_thread(serialThread, ())
		# remove the menu item
		# menus["main"]["items"].pop(6)
		# menus["main"]["focus"] = 0
		serialThread()
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
		#try:
		#	temp = get_temp()
		#	last_temp = temp
		#except:
		#	temp = last_temp
		#try:
		#	tds_value = get_tds()
		#	last_ppm = tds_value
		#except:
		#	tds_value = last_ppm
		#print("{\"temp\":" + str(temp) + ",\"ppm\":" + str(tds_value) + "}")
		#print(json.dumps({"type": "sensor", "temp": temp, "ppm": tds_value}))
		packet = {"type": "sensor"}
		for sensorName in sensors:
			try:
				packet[sensorName] = sensors[sensorName]["read"]()
			except:
				packet[sensorName] = None
		print(json.dumps(packet))
		
		##
		## INPUT
		##
		
		read, _, _ = select.select([sys.stdin], [], [], 0)
		if sys.stdin in read:
			inputdata = sys.stdin.readline().strip()
			if inputdata:
				try:
					data = json.loads(inputdata)
					if data["type"] == "list_files":
						#print("{\"type\": \"no\"}")
						send = {"type": "list_files", "files": []}
						for (filename, isdir, size, mtime, sha256) in listdir(data["path"]):
							send["files"].append({"filename": filename, "isDir": isdir, "size": size})
						print(json.dumps(send))
					elif data["type"] == "scan_networks":
						nic.active(True)
						send = {"type": "scan_networks", "networks": [], "current": { "ssid": nic.config("ssid") }}
						nets = nic.scan()
						for net in nets:
							send["networks"].append({"ssid": net[0], "rssi": net[3], "security": net[4]})
						print(json.dumps(send))
				except Exception as e:
					print(json.dumps({"type": "error", "error": e}))
		if btnOK.value():
			break
		time.sleep(1)

def get_file_stats(filename):
	stat = os.stat(filename)
	size = stat[6]
	mtime = stat[8]
	return (size, mtime, '')

def listdir(directory):
	files = os.ilistdir(directory)
	out = []
	for (filename, filetype, inode, _) in files:
		fn_full = "/" + filename if directory == '/' else directory + '/' + filename
		isdir = filetype == 0x4000
		if isdir:
			out.append((fn_full, isdir, 0, 0, ''))
		else:
			file_stats = get_file_stats(fn_full)
			out.append((fn_full, isdir) + file_stats)
	return sorted(out)

def networkOutput():
	pass

#serialThread()
# _thread.start_new_thread(serialThread, ())

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