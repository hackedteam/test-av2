import os
import sys
import smtplib
import datetime

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#from ..web.models import Report as DBReport, db
from ..web.models import Test, Result, db


class Report:
	def __init__(self, test_id=None): #, results=None):
		self.test_id = test_id
		self.results = self._get_results()

	def save_file(self, filename):
		if self.report is None:
			print "[report:savefile] Report can't be None"
			return False
		try:
			print "[*] RESULTS: \n%s" % self.report 

			# ordered = {}
			with open( filename, "wb") as f:
				f.write("REPORT\n")
				f.write(self.report)
		except Exception as e:
			print "[report:save_file] Impossible save file. Exception: %s" % e
			return False

	def _get_results(self):
		results = Result.query.filter_by(test_id=self.test_id)
		if results is not None:
			rs = []
			for result in results:
				r = "%s, %s, %s" % (result.vm_name, result.kind, result.result.split(", ")[-1])
#				r['name'] = result.vm_name
#				r[result.kind] = result.result.split(", ")[-1]
				rs.append(r)
			return rs
		else:
			print "DBG No results for test with id %s." % self.test_id 
			return None
	
	def send_mail(self, result):
		if self.report is None:
			return False
		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			body = MIMEText(result)
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			#smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.sendmail(msg["From"], msg["To"], msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False


	def _build_mail_body(self):
		hcolumns = ['name']

		host = "172.20.20.167"
		port = "8000"

		report_file = "http://%s:%s/report/%s" % ( host, port, self.test_id )

		res = Result.query.filter_by(test_id=self.test_id).order_by(Result.vm_name)

		if res is None:
			print "DBG Results are None"
			return None
		results = []
		vms = []
		hcolumns = ['name']
		result = {}

		for r in res:
			if r.vm_name not in vms:
				if result != {}:
					results.append(result)
				result = {}
				vms.append(r.vm_name)
				result['name'] = r.vm_name				

			if r.kind not in hcolumns:
				hcolumns.append(r.kind)

			result[r.kind] = r.result.split(", ")[-1]

		# se alla fine del for vuoto vuol dire che avevo una sola vm
		if results == []:
			results.append(result)

		print "DBG results %s" % results
		print "DBG hcolumns %s" % hcolumns
		style  = """
<html>
<style type'text/css'>
#success-div {
    background-color: green;
    width: 20px;
    height: 10px;
}
#error-div {
    background-color: black;
    width: 20px;
    height: 10px;
}
#failed-div {
    background-color: red;
    width: 20px;
    height: 10px;
}
#blacklisted-div {
	background-color: grey;
	width: 20px;
	height: 10px;
}
a.fill-div {
    display: block;
    height: 100%;
    width: 100%;
    text-decoration: none;
}
</style>
<body>		
		"""

		header_st = "<table><tr>"
		header_en = "</tr>"
		linestart = "<tr><td>%s</td>"
		linetoken = "<td id='%s-div'><a href='%s' class='fill-div'></a></td>"
		lineend   = "</tr>"
		legend    = "</table><p>Legend:</p><table><tr><td id=success-div></td><td>SUCCESS</td><tr><td id=failed-div></td><td>FAILED</td><tr><td id=error-div></td><td>ERROR</td><tr><td id=blacklisted-div></td><td>BLACKLISTED</td></tr></table>"
		footer    = "<br><br><b>View full <a href='%s'>report</a><b></body></html>" % report_file

		content = style 

		header = header_st

		for col in hcolumns:
			header += "<td>%s</td>" % col

		header += header_en
		content += header

		for res in results:
			print "DBG res is %s" % res
			avname = res['name']
			l = linestart % avname
			for col in hcolumns[1:]:
				link = "http://%s:%s/report/%s/result/%s/%s" % (host, port, self.test_id, avname, col)

				for kind in ["FAILED", "BLACKLISTED", "SUCCESS", "ERROR"]:
					if kind in res[col]:
						l += linetoken % (kind.lower(), link)
						break
					elif "STARTED" in res[col] or res[col] == "n":
						print "DBG found line STARTED"
						l += linetoken % ("error", link)
						break
				
			l += lineend
			content += l

		content += legend
		content += footer

		return content

	def send_report_color_mail(self):
		content = self._build_mail_body()

		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor Results"
			msg["From"] = "avmonitor@hackingteam.com"
			#msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com,alor@hackingteam.com,g.landi@hackingteam.com"
			msg["To"] = "olli@hackingteam.com"
			body = MIMEText(content, 'html')
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False