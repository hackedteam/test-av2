import os
import sys
import smtplib
import datetime

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from ..web.models import db

class Report:
	def __init__(self, test_id=None, results=None):
		self.test_id = test_id
		self.results = results
		
		if results != None:
			self.report = self._prepare_report()
		else:
			self.report = None


	def _prepare_report(self):
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
			#smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.sendmail(msg["From"], msg["To"], msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False


	def _build_mail_body(self,  url_dir):

		hresults = []
		hcolumns = ['name']

		host = "172.20.20.167"
		port = "8000"

		report_file = "http://%s:%s/report/%s" % ( host, port, self.test_id )

		res = [ x for x in self.results if len(x)>0 and len(x[0])>0 ]

		sortedresults = sorted(res, key = lambda x: x[0][0])
		print "DBG sorted %s" % sortedresults

		for av in sortedresults:
			name = av[0].split(",")[0]
			#k = len(av)

			hres = []
			hres.append(name)

			for ares in av:
				r = ares.split(", ")
				hres.append(r[-1])
				if r[1] not in hcolumns:
					hcolumns.append(r[1])

			hresults.append(hres)


		print "DBG hresults %s" % hresults
		style  = """<html><head><style type'text/css'>
#suc { background-color: green; width: 10px; height: 10px; }
#err { background-color: black; width: 10px; height: 10px; }
#fai { background-color: red; width: 10px; height: 10px; }
#bla { background-color: grey; width: 10px; height: 10px; }
a.fill { display: block; height: 100%; width: 100%; text-decoration: none; }
</style></head>"""		

		'''
		style  = """<html><style type'text/css'>
#suc-div { background-color: green; width: 10px; height: 10px; }
#err-div { background-color: black; width: 10px; height: 10px; }
#fai-div { background-color: red; width: 10px; height: 10px; }
#bla-div { background-color: grey; width: 10px; height: 10px; }
a.fill-div { display: block; height: 100%; width: 100%; text-decoration: none; }
</style><body>"""


		header_st = "<table>\n  <tr>\n"
		header_en = "  </tr>\n"
		linestart = "  <tr><td>%s</td>"
		linetoken = "    <td id='%s-div'><a href='%s' class='fill-div'></a></td>\n"
		lineend   = "  </tr>\n"
		legend    = "</table>\n<p>Legend:</p>\n<table><tr><td id=success-div></td><td>SUCCESS</td><tr><td id=failed-div></td><td>FAILED</td><tr><td id=error-div></td><td>ERROR</td><tr><td id=blacklisted-div></td><td>BLACKLISTED</td></tr></table>\n"
		footer    = "<br><br><b>View full <a href='%s'>report</a><b></body></html>" % report_file
		'''

		header_st = "<body><table><tr>"
		header_en = "</tr>"
		linestart = "<tr><td>%s</td>"
		linetoken = "<td id='%s'><a href='%s' class='fill'></a></td>"
		lineend   = "</tr>"
		legend    = "</table><p>Legend:</p><table><tr><td id=suc></td><td>SUCCESS</td><tr><td id=fai></td><td>FAILED</td><tr><td id=err></td><td>ERROR</td><tr><td id=bla></td><td>BLACKLISTED</td></tr></table>"
		footer    = "<br><br><b>View full <a href='%s'>report</a><b></body></html>" % report_file

		content = style 

		header = header_st

		for col in hcolumns:
			header += "<td>%s</td>" % col # col.replace("exploit_","")

		header += header_en
		content += header

		for res in hresults:
			rd = dict(zip(hcolumns,res))
			print "DBG rd %s" % rd
			#rd['name'], rd['silent'], rd['melt'], rd['exploit']
			avname = rd['name']
			l = linestart % avname
			for col in hcolumns[1:]:
				link = "http://%s:%s/report/%s/result/%s/%s" % (host, port, self.test_id, avname, col)

				found = False
				for kind in ["FAILED", "BLACKLISTED", "SUCCESS", "ERROR"]:
					print "DBG parsing rd[%s]" % col  
					if kind in rd[col]:
						l += linetoken % (kind.lower()[0:3], link)
						found = True
						break
					elif "STARTED" in rd[col]: #or rd[col] == "n":
						print "DBG found line STARTED"
#						l += linetoken % ("error", link)
						l += linetoken % ("err", link)
						found = True
						break
				if not found:
					print "DBG found nothing. assuming ERROR"
#					l += linetoken % ("error", link)
					l += linetoken % ("err", link)
			l += lineend

			content += l

		content += legend
		content += footer

		return content

	def send_report_color_mail(self,  url_dir):
		content = self._build_mail_body(url_dir)

		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor Results"
			msg["From"] = "avmonitor@hackingteam.com"
			#msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com,alor@hackingteam.com,g.landi@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			#msg["To"] = "olli@hackingteam.com"
			print "CONTENT LENGTH: %s" % len(content)
			body = MIMEText(content, 'html')
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False