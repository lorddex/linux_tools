#!/usr/bin/python
# script that adds a VM who requests an IP address using the dhcpd to local hosts file
import sys
import subprocess
import string
import time

debug_file="/var/log/add_hosts.log"

def debug(message):
	message = time.strftime("%d %b %Y %H:%M:%S") + " " + message 
	print message
	fd = open(debug_file, "a")
	fd.write(message + "\n")
	fd.close()

text=""
for arg in sys.argv:
	text = text +" "+arg
debug(text)	

action=sys.argv[1]
ip=sys.argv[3]
mac=sys.argv[2]
hosts="/etc/hosts"

# if del action is called exit from this script
if action == "del":
#	fd=open(hosts, "r")
#	hosts_lines=fd.readlines()
#	fd.close()
	
#	fd=open(hosts, "w")
#	for line in hosts_lines:
#		if ip not in line:
#			fd.write(line)

#	debug( "Ok, %s deleted from %s file" % (name, hosts))
	sys.exit(0)		

# add address to local hosts file 
#command = ["/bin/ps", "-eo", "command"]
#process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=9192)

if len(sys.argv) == 5:
	name = sys.argv[4]
	debug("host name from parameters: "+name)
else:
	command = "ps axo pid,command | grep /usr/bin/kvm"
	process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	found = None
	for line in process.stdout.readlines():
		pid=line.split(" ")
		pid = pid[0]
		fd_c = open("/proc/"+pid+"/cmdline", "r")
		lines=fd_c.readlines()
		fd_c.close()
		if len(lines)>0:
			line=lines[0]
			line=string.replace(line, "-", " -")
			line=string.replace(line, "\x00", " ")
		else:
			continue
		if mac in line and "add_host" not in line:
			found = line
			break
	if found is None:
		debug("Ops, no VM with %s found" % mac)
		sys.exit(1)
	parms = found.split(" -")[1:]
	name=False

	for par in parms:
		if par.strip().startswith("name"):
			name = par.strip().split(" ")[1]

if name is False:
	debug("Ops, VM name not found")
	sys.exit(2)

fd=open(hosts, "r")

hosts_lines=fd.readlines()
fd.close()
already=False
for line in hosts_lines:
	if name in line:
		already=line
		break
change=False
if already is not False:
	if ip in line:
		debug("Ok, VM already in hosts file")
		sys.exit(0)
	else:
		change=True
	
if change is False:
	fd=open(hosts, "a")
	fd.write(ip + "\t\t" + name +"\n")
else:
	fd=open(hosts, "w")
	for line in hosts_lines:
		if name in line:
			line = ip + "\t\t" + name + "\n"
		fd.write(line)

fd.close()

debug( "Ok, %s added to %s file" % (name, hosts))
