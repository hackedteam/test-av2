import redis
import socket

if "winxp" in socket.gethostname():
	channel = socket.gethostname().replace("winxp","")
else:
	channel = socket.gethostname().replace("win7","")
r = redis.Redis("10.0.20.1")
r.publish(channel, "STARTED")
