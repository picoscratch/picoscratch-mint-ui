from display import oled
from time import sleep
import os
import json
import select
import sys
from sensor import read_sensors

def mergeDicts(x, y):
	z = x.copy()   # start with keys and values of x
	z.update(y)    # modifies z with keys and values of y
	return z

def serialThread(btnOK, nic):
	oled.fill(0)
	oled.text("Daten ueber USB", 0, 0, 1)
	oled.text("OK zum beenden", 0, 10, 1)
	oled.show()
	sleep(1)
	while True:
		# packet = {"type": "sensor"}
		# for sensorName in sensors:
		# 	try:
		# 		packet[sensorName] = sensors[sensorName]["read"]()
		# 	except:
		# 		packet[sensorName] = None
		# print(json.dumps(packet))
		sensors = read_sensors()
		simplifiedSensors = {}
		for sensor in sensors:
			simplifiedSensors[sensor["id"]] = sensor["value"]
		print(json.dumps(mergeDicts({"type": "sensor"}, simplifiedSensors)))
		
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
		sleep(1)

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