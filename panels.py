import time
from sensor import read_sensors
from display import invertArea

allPanels = ["temp", "ppm"]
panels = []
selectedPanel = 0
panelheight = 30
lastI2Cids = []
btnSleep = 0.3

def gauge(oled, v, maxv, x, y, w, h, minv=0):
	a = (v - minv) / (maxv - minv)
	a = a * w
	oled.rect(x, y, w, h, 1)
	oled.rect(x, y, int(a), h, 1, True)  # type: ignore

def drawPanels(oled, sensors, i2c, ledRed, ledYellow, ledGreen, display_width, display_height):
	# global panels
	# global lastI2Cids
	global panels
	panels = []
	oled.fill(0)
	i = 0
	
	# Legacy sensors
	# for panel in allPanels:
	# 	h = i*panelheight + 2
	# 	# if i > 0:
	# 	# 	h = h + 3
	# 	# scroll the height away depending on the selected panel
	# 	h = h - (selectedPanel * panelheight)
	# 	if selectedPanel % 2 != 0:
	# 		h = h + panelheight
		
	# 	oled.rect(0, h, display_width, panelheight, 1)

	# 	if panel == "add":
	# 		oled.text("Neuer Sensor...", 5, 5+h, 1)
	# 	else:
	# 		value = 0
	# 		unit = ""
	# 		min = 0
	# 		max = 0
	# 		friendlyName = panel
	# 		if panel in sensors:
	# 			value = sensors[panel]["read"]()
	# 			unit = sensors[panel]["unit"]
	# 			min = sensors[panel]["min"]
	# 			max = sensors[panel]["max"]
	# 			friendlyName = sensors[panel]["friendlyName"] if "friendlyName" in sensors[panel] else panel
	# 			#if i == selectedPanel:
	# 			#	#if value == None:
	# 			#	#	ledRed.duty_u16(0)
	# 			#	#	ledYellow.off()
	# 			#	#	ledGreen.off()
	# 			#	#else:
	# 			#		#trafficLight(value, sensors[panel]["good"], sensors[panel]["warn"], sensors[panel]["bad"], sensors[panel]["toolow"])

	# 		if value == None:
	# 			#oled.text("Nicht verbunden", 5, 5+h+10, 1)
	# 			continue
	# 		else:
	# 			panels.append(panel)
	# 			oled.text(friendlyName, 5, 5+h, 1)
	# 			text = str(value) + unit
	# 			# right aligned, every char is 8px wide
	# 			oled.text(text, display_width - (len(text) * 8) - 5, 5+h, 1)

	# 			gauge(oled, value, max, 5, 5+h+10, display_width - 10, 10, min)
	# 	if i == selectedPanel:
	# 		invertArea(oled, 0, h, display_width, panelheight)
	# 	i = i + 1
	
	# i2c_ids = i2c.scan()
	# # I2C Sensors
	# for sensorID in sensors:
	# 	sensor = sensors[sensorID]
	# 	if not "isI2C" in sensor:
	# 		continue
	# 	if not sensor["addr"] in i2c_ids:
	# 		continue
	# 	if not sensor["addr"] in lastI2Cids:
	# 		sensor["init"](i2c)
	# 	h = i*panelheight + 2
	# 	# if i > 0:
	# 	# 	h = h + 3
	# 	# scroll the height away depending on the selected panel
	# 	h = h - (selectedPanel * panelheight)
	# 	if selectedPanel % 2 != 0:
	# 		h = h + panelheight
		
	# 	oled.rect(0, h, display_width, panelheight, 1)
		
	# 	value = 0
	# 	unit = ""
	# 	min = 0
	# 	max = 0
	# 	friendlyName = panel
	# 	value = sensor["read"]()
	# 	unit = sensor["unit"]
	# 	min = sensor["min"]
	# 	max = sensor["max"]
	# 	friendlyName = sensor["friendlyName"]
	# 	if i == selectedPanel:
	# 		if value == None:
	# 			ledRed.duty_u16(0)
	# 			ledYellow.off()
	# 			ledGreen.off()
	# 		else:
	# 			#trafficLight(value, sensor["good"], sensor["warn"], sensor["bad"], sensor["toolow"])
	# 			if value < sensor["good"]:
	# 				ledGreen.on()
	# 				ledYellow.off()
	# 				ledRed.duty_u16(0)
	# 			elif value > sensor["bad"]:
	# 				ledRed.duty_u16(255*255)
	# 				ledGreen.off()
	# 				ledYellow.off()
	# 			else:
	# 				ledYellow.on()
	# 				ledRed.duty_u16(0)
	# 				ledGreen.off()
		
	# 	panels.append(sensorID)
	# 	oled.text(friendlyName, 5, 5+h, 1)
	# 	if value == None:
	# 		text = "..."
	# 		value = 0
	# 	else:
	# 		text = str(value) + unit
	# 	# right aligned, every char is 8px wide
	# 	oled.text(text, display_width - (len(text) * 8) - 5, 5+h, 1)
		
	# 	gauge(oled, value, max, 5, 5+h+10, display_width - 10, 10, min)
	# 	if i == selectedPanel:
	# 		invertArea(oled, 0, h, display_width, panelheight)
	# 	i = i + 1
	
	# lastI2Cids = i2c_ids

	sensors = read_sensors()

	for sensor in sensors:
		if sensor["isI2C"] == False and sensor["value"] == None:
			continue
		h = i*panelheight + 2
		# if i > 0:
		# 	h = h + 3
		# scroll the height away depending on the selected panel
		h = h - (selectedPanel * panelheight)
		if selectedPanel % 2 != 0:
			h = h + panelheight
		
		oled.rect(0, h, display_width, panelheight, 1)

		friendlyName = sensor["friendlyName"]
		value = sensor["value"]
		unit = sensor["unit"]
		min = sensor["min"]
		max = sensor["max"]
		friendlyName = sensor["friendlyName"]
		if i == selectedPanel:
			if value == None:
				ledRed.duty_u16(0)
				ledYellow.off()
				ledGreen.off()
			else:
				#trafficLight(value, sensor["good"], sensor["warn"], sensor["bad"], sensor["toolow"])
				if value < sensor["traffic"]["good"]:
					ledGreen.on()
					ledYellow.off()
					ledRed.duty_u16(0)
				elif value > sensor["traffic"]["bad"]:
					ledRed.duty_u16(255*255)
					ledGreen.off()
					ledYellow.off()
				else:
					ledYellow.on()
					ledRed.duty_u16(0)
					ledGreen.off()
		
		panels.append(sensor["id"])
		oled.text(friendlyName, 5, 5+h, 1)
		if value == None:
			text = "..."
			value = 0
		else:
			text = str(value) + unit
		# right aligned, every char is 8px wide
		oled.text(text, display_width - (len(text) * 8) - 5, 5+h, 1)
		
		gauge(oled, value, max, 5, 5+h+10, display_width - 10, 10, min)
		if i == selectedPanel:
			invertArea(oled, 0, h, display_width, panelheight)
		i = i + 1
	
	# If no sensors are attached
	if len(panels) == 0:
		ledRed.duty_u16(0)
		ledYellow.off()
		ledGreen.off()
		oled.fill(0)
		h = int(display_height/2-(panelheight/2))
		oled.rect(0, h, display_width, panelheight, 1)
		oled.text("Verbinde einen", 5, 5+h)
		oled.text("Sensor", 5, 15+h)
	oled.show()

def handlePanelButtons(btnLeft, btnOK, btnRight, btnBack):
	global selectedPanel
	if btnLeft.value():
		selectedPanel = selectedPanel - 1
		if selectedPanel < 0:
			selectedPanel = len(panels) - 1
		#drawPanels()
		time.sleep(btnSleep)
	elif btnRight.value():
		selectedPanel = selectedPanel + 1
		if selectedPanel > len(panels) - 1:
			selectedPanel = 0
		#drawPanels()
		time.sleep(btnSleep)
	elif btnBack.value():
		#if panels[selectedPanel] == "add":
		#	sensor = menus["sensors"]["items"][askQuestion("sensors")]
		#	if sensor == "exit":
		#		return False
		#	panels.insert(len(panels) - 1, sensor)
		#else:
		#	panels.pop(selectedPanel)
		#drawPanels()
		#time.sleep(btnSleep)
		return False
	if selectedPanel > len(panels) - 1:
		selectedPanel = len(panels) - 1
	return True
