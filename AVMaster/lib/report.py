from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib


class Report:
	def __init__(self, filename=None, results=None):
		self.filename = filename
		self.results = results
		
		if results != None:
			self.report = self.get()
		else:
			self.report = None


	def get(self):
		r = ""
		for l in self.results:
			print "%s" % l
			r+=l
		return r

	def save_file(self):
		if self.report is None:
			print "[report:savefile] Report can't be None"
			return False
		try:
			print "[*] RESULTS: \n%s" % self.report 

			# ordered = {}
			with open( self.filename, "wb") as f:
				f.write("REPORT\n")
				f.write(self.report)
		except Exception as e:
			print "[report:save_file] Impossible save file. Exception: %s" % e
			return False
	
	def send_mail(self):
		if self.report is None:
			return False
		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			body = MIMEText(self.report)
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
		except Exception as e:
			print "[report:send mail] Impossible send report via mail. Exception: %s" % e
			return False
	

if __name__ == "__main__":
	r = Report()

	s = Report('/tmp/bobby.txt',["GooD","b4d"])
	# bad report class
	assert r.save_file() is False
	#assert r.send_mail() is False
	# good report class
	assert s.save_file() is None
	#assert s.send_mail() is True
