import os


log_file = "/var/log/rcs.log"

if os.path.exists(log_file):
	with open(log_file, "r") as f:
		cont = f.read()

		if "RCS-SYNC" in cont:
			print "--- INFECTED MACHINE DETECTED ---"
			''' TODO: do something '''

