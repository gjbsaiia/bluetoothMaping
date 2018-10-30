#!/usr/bin/python
import os
import sys
import subprocess
import signal
import time
from manifest import bluDev
from py_compile import compile

def main():
	if(len(sys.argv) < 2):
		i = 1
		addresses = []
		while i < len(sys.argv):
			addresses.append(sys.argv[i])
			i += 1
		rssi = searchAddresses(addresses)
		print(rssi)
	generateFreshLog()
	connectable = getConnectable()
	updateManifest(connectable)

def searchAddresses(addresses):
	rssi = []
	for each in addresses:
		try:
			val = bluDev[each][1]
		except KeyError:
			val = 1000
		rssi.append(val)
	return rssi

def generateFreshLog():
	path = "raw_log.txt"
	with open(path, "w+") as file:
		i = 1
	file.close()
	startScan = "sudo ./beacon-scan.sh > /dev/null 2>&1"
	scan = subprocess.Popen(startScan, shell=True, preexec_fn=os.setsid)
	startLog = "sudo hcidump > ~/Documents/projects/bluetoothSpammer/raw_log.txt"
	log = subprocess.Popen(startLog, shell=True, preexec_fn=os.setsid)
	time.sleep(10)
	os.killpg(os.getpgid(log.pid), signal.SIGTERM)
	os.killpg(os.getpgid(scan.pid), signal.SIGTERM)

def returnMACs(name):
	keys = []
	for key in bluDev:
		if(bluDev[key][0] == name):
			keys.append(key)
	return keys

def getConnectable():
	rawLog = "raw_log.txt"
	lines = []
	with open(rawLog) as file:
		lines = file.readlines()
	file.close()
	incomingDevs = []
	i = -1
	flag = False
	for line in lines:
		if("> HCI Event:" in line):
			if(not flag):
				flag = True
			incomingDevs.append([])
			i += 1
		if(line[0] == "<"):
			flag = False
		if(flag):
			newLine = removeHCIFormat(line)
			incomingDevs[i].append(newLine)
	connectable = []
	snagged = {}
	j = 0
	flag = False
	update = False
	for dev in incomingDevs:
		name = ""
		RSSI = ""
		bdaddr = ""
		for line in dev:
			if("ADV_IND" in line or "SCAN_RSP" in line):
				flag = True
			if("RSSI: " in line):
				splitt = line.split("RSSI: ")
				RSSI = splitt[1]
			if("bdaddr" in line):
				splitt = line.split(" ")
				bdaddr = splitt[len(splitt) - 2]
				if(bdaddr in snagged):
					update = True
					flag = False
				else:
					snagged[bdaddr] = j
			if("local name" in line):
				splitt = line.split("'")
				name = splitt[1]
		if(flag):
			flag = False
			update = False
			if(name == ""):
				name = "unknown"
			connectable.append([bdaddr, name, RSSI])
			j += 1
		if(update):
			update = False
			flag = False
			try:
				index = snagged[bdaddr]
				if(name == ""):
					name = connectable[index][1]
				if(RSSI == ""):
					RSSI = connectable[index][2]
				connectable[snagged[bdaddr]] = (bdaddr, name, RSSI)
			except IndexError:
				print("problematic index: "+str(snagged[bdaddr]))
				print(snagged)
				print("length of array: "+str(len(connectable)))
				print(connectable)
				raise KeyboardInterrupt
	j = 0, i = 0
	return connectable

def removeHCIFormat(line):
	l = line.lstrip()
	l = l.replace("\n", "")
	l = l.replace("> ", "")
	return l

def updateManifest(web):
	resetCycle = False
	cycle = 0
	path = "manifest.py"
	with open(path, "r") as file:
		lines = file.readlines()
	file.close()
	i = 0
	newlines = []
	addrs = {}
	for line in lines:
		if "cycle = " in line:
			splitt = line.split("cycle = ")
			cycle = int(splitt[1].strip("\n"))
			if(cycle == 10):
				resetCycle = True
				newline = "cycle = 0\n"
				cycle = 0
			else:
				newline = "cycle = "+str(cycle+1)+"\n"
				cycle += 1
			newlines.append(newline)
		else:
			newlines.append(line)
		i += 1
		if "bluDev = {" in line:
			break
	j = i
	while(i < len(lines)):
		if "#x" in lines[i]:
			break
		else:
			if(not resetCycle):
				splitt = lines[i].split(":[")
				addr = splitt[0].strip('"')
				splitt = splitt[1].split(", ")
				thisCycle = int(splitt[2].split(']')[0])
				if(thisCycle > cycle - 3):
					addrs[addr] = j
					newlines.append(lines[i])
					j += 1
			i += 1
	for each in web:
		if( each[0] in addrs ):
			newlines[addrs[each[0]]] = '"'+each[0]+'":'+'["'+each[1]+'", '+each[2]+', '+str(cycle)+'],\n'
		else:
			newlines.append('"'+each[0]+'":'+'["'+each[1]+'", '+each[2]+', '+str(cycle)+'],\n')
	while i < len(lines):
		newlines.append(lines[i])
		i += 1
	with open(path, "w+") as file:
		for line in newlines:
			file.write(line)
	file.close()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print
		print 'oops... interrupted \_[o.O]_/'
		try:
		    sys.exit(0)
		except SystemExit:
		    os._exit(0)
