import os
import sys
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


class Report:
	def __init__(self, filename=None, html_file=None, results=None):
		self.filename = filename
		self.html_file = html_file
		self.results = results
		
		if results != None:
			self.report = self.prepare_report()
		else:
			self.report = None


	def prepare_report(self):
		r = ""
		for l in self.results:
			if l is list:
				for el in l:
					print "  %s\n" % el
					r+= "  %s\n" % el
			else:
				print "%s\n" % l
				r+= "%s\n" % l
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

	def parse_results(self,filename):

		success = []
		errors  = []
		failed  = []

		with open(filename, 'rb') as f:
			
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
							'''
							res['av'] = j[1]
							res['kind'] = j[0]
							'''
							res['result'] = j[3].split(":")[2][3:-2].replace("+","")

							if "SUCCESS" in j[3]:
								success.append(res)
							else:
								failed.append(res)
				except:
					if "ERROR" in l:
						errors.append(l)
					#print "failed: %s" % e
					pass
		return success,errors,failed

	def add_header(self, name):
		html_head  = "<h2>%s</h2>" % name
		html_head += html_table_open
		return html_head

	def add_results(self, res):
		html_results = ""

		for s in res:
			html_table = html_section
			html_table = html_table.replace("AV_NAME",s['av'])
			html_table = html_table.replace("AV_KIND",s['kind'])
			html_table = html_table.replace("AV_RESULT",s['result'])
			html_table = html_table.replace("AV_TXT_LINK","results_%s_%s.txt" % (s['av'],s['kind']) )
			html_table = html_table.replace("AV_SCREEN_LINK","screenshot_%s_%s.png" % (s['av'],s['kind']) )
			html_results += html_table
		return html_results

	def add_errors(self, errors):
		html_errs = ""
		for e in errors:
			html_errs += e
		return html_errs



	def write_html_report(self, results, html_file_name):
		html_table_open = '''
		<table border=1 cellpadding=1 cellspacing=2 width=70%>
			<tr><td with=15%>Virtual Machine</td>
				<td with=15%>Kind of test</td>
				<td width=50%>Result</td>
				<td width=10%>TXT Report</td>
				<td width=10%>Screenshot</td></tr>
		'''

		html_table_closed = '</table>'

		html_section = '''
		<tr><td>AV_NAME</td>
			<td>AV_KIND</td>
			<td>AV_RESULT</td>
			<td><a href="AV_TXT_LINK">txt report</td>
			<td><a href="AV_SCREEN_LINK">screenshot</td></tr>
		'''

		success,errors,failed = results

		with open(html_file_name, 'wb') as f:
			f.write("<html><body>")

			f.write( self.add_header("Failed") )
			f.write( self.add_results(failed) )
			f.write( self.html_table_closed)

			f.write( "<h2>Errors</h2>")
			f.write( self.add_errors(errors) )

			f.write( self.add_header("Success") )
			f.write( self.add_results(success) )
			f.write( self.html_table_closed)

			f.write("</body></html>")

	def save_html(self):
			results = self.parse_results(self.filename)

			self.write_html_report(results, self.html_file)

	
	def send_mail(self):
		if self.report is None:
			return False
		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			#msg["To"] = "olli@hackingteam.com"
			body = MIMEText(self.report)
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			#smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.sendmail(msg["From"], msg["To"], msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False
	

if __name__ == "__main__":
	r = Report()

	s = Report('/tmp/bozz',["GooD","b4d"])
	# bad report class
	assert r.save_file() is False
	#assert r.send_mail() is False
	# good report class
	assert s.save_file() is None
	assert s.send_mail() is True
