import os
import sys

f = open('/tmp/bozz', 'rb')

success = []
errors  = []
failed  = []

g = 0 

for l in f.readlines():
	try:
		e=eval(l)
		for k in e:
			j = k.split(",")
			#print j

			if "SUCCESS" in j[3] or "FAILED" in j[3]:
				#j[0],j[1],j[3]
				res = {}
				res['av'] = j[0]
				res['kind'] = j[1]
				res['result'] = j[3]

				if "SUCCESS" in j[3]:
					success.append(res)
				else:
					failed.append(res)
	except:
		if "ERROR" in l:
			errors.append(l)
		#print "failed: %s" % e
		pass


print "Success: %s" % success
print "Failed: %s" % failed
print "Errors: %s" % errors

print "tot success %s" % len(success)
print "tot errors %s" % len(errors)
print "tot failed %s" % len(failed)
print "tot results: %s" % (len(success)+len(errors)+len(failed))
