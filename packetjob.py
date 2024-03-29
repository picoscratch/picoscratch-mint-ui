from display import oled, readPBM
from time import sleep
import os
import json
import select
import sys
from sensor import read_sensors
from util import get_serial, mergeDicts
import socket
import network

def handlePacket(data):
	if data["type"] == "list_files":
		#print("{\"type\": \"no\"}")
		send = {"type": "list_files", "files": []}
		for (filename, isdir, size, mtime, sha256) in listdir(data["path"]):
			send["files"].append({"filename": filename, "isDir": isdir, "size": size})
		return json.dumps(send)
	elif data["type"] == "scan_networks":
		nic = network.WLAN(network.STA_IF)
		nic.active(True)
		send = {"type": "scan_networks", "networks": [], "current": { "ssid": nic.config("ssid") }}
		nets = nic.scan()
		for net in nets:
			send["networks"].append({"ssid": net[0], "rssi": net[3], "security": net[4]})
		return json.dumps(send)
	elif data["type"] == "read_file":
		return json.dumps({"type": "read_file", "content": open(data["path"], "r").read()})
	elif data["type"] == "write_file":
		f = open(data["path"], "w")
		f.write(data["content"])
		f.close()
		return json.dumps({"type": "write_file", "content": data["content"]})
	elif data["type"] == "delete_file":
		os.remove(data["path"])
		return json.dumps({"type": "delete_file"})
	return json.dumps({"type": "error", "error": "unknown type"})

def serialThread(btnOK, nic):
	oled.fill(0)
	# oled.text("Daten ueber USB", 0, 0, 1)
	# oled.text("OK zum beenden", 0, 10, 1)
	oled.blit(readPBM("usbmode.pbm"), 0, 0)
	oled.show()
	sleep(1)
	serial = get_serial()
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
		print(json.dumps(mergeDicts({"type": "sensor", "serial": serial}, simplifiedSensors)))
		
		##
		## INPUT
		##
		
		read, _, _ = select.select([sys.stdin], [], [], 0)
		if sys.stdin in read:
			inputdata = sys.stdin.readline().strip()
			if inputdata:
				try:
					data = json.loads(inputdata)
					print(handlePacket(data))
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

def networkOutput(btnOK, nic):
	oled.fill(0)
	oled.blit(readPBM("connecting.pbm"), 0, 0)
	oled.show()
	sleep(1)
	sock = socket.socket()
	sock.connect(socket.getaddrinfo("mint.picoscratch.de", 2737)[0][-1])
	sock.setblocking(0)
	serial = get_serial()
	oled.fill(0)
	# oled.text("Daten ueber NET", 0, 0, 1)
	# oled.text("OK zum beenden", 0, 10, 1)
	oled.blit(readPBM("netmode.pbm"), 0, 0)
	oled.text(serial, 0, 20, 1)
	oled.show()
	while True:
		sensors = read_sensors()
		simplifiedSensors = {}
		for sensor in sensors:
			simplifiedSensors[sensor["id"]] = sensor["value"]
		sock.send(json.dumps(mergeDicts({"type": "sensor", "serial": serial}, simplifiedSensors)))
		
		##
		## INPUT
		##

		sleep(0.5)

		try:
			data = sock.recv(1024)
			print(data)
			sock.send(handlePacket(json.loads(data)))
		except Exception as e:
			# print(e)
			pass # no data to read
		
		# read, _, _ = select.select([sock], [], [], 0)
		# if sock in read:
		# 	inputdata = sock.readline().strip()
		# 	if inputdata:
		# 		try:
		# 			data = json.loads(inputdata)
		# 			if data["type"] == "list_files":
		# 				#print("{\"type\": \"no\"}")
		# 				send = {"type": "list_files", "files": []}
		# 				for (filename, isdir, size, mtime, sha256) in listdir(data["path"]):
		# 					send["files"].append({"filename": filename, "isDir": isdir, "size": size})
		# 				sock.send(json.dumps(send))
		# 			elif data["type"] == "scan_networks":
		# 				nic.active(True)
		# 				send = {"type": "scan_networks", "networks": [], "current": { "ssid": nic.config("ssid") }}
		# 				nets = nic.scan()
		# 				for net in nets:
		# 					send["networks"].append({"ssid": net[0], "rssi": net[3], "security": net[4]})
		# 				sock.send(json.dumps(send))
		# 		except Exception as e:
		# 			sock.send(json.dumps({"type": "error", "error": e}))
		if btnOK.value():
			break
		sleep(0.5)