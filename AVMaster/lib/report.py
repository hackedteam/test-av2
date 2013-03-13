import os
import sys
import smtplib
import datetime

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


class Report:
	def __init__(self, results=None):
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

	def _parse_results(self,filename):

		success = []
		errors  = []
		failed  = []

		with open(filename, 'rb') as f:
			
			for l in f.readlines():
				try:
					e=eval(l)
					for k in e:
						j = k.split(",")
						print j

						if "SUCCESS" in j[3] or "FAILED" in j[3]:
							print j[0],j[1],j[3].split(":")[2][3:-2].replace("+","")
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
								print len(success)
							else:
								failed.append(res)
								print len(failed)
				except:
					if "ERROR" in l:
						errors.append(l)
						print len(errors)
					#print "failed: %s" % e
					pass
		return success,errors,failed

	def _add_header(self, name):
		
		html_table_open = '''
		<table border=1 cellpadding=1 cellspacing=2 width=70%>
			<tr><td with=15%>Virtual Machine</td>
				<td with=15%>Kind of test</td>
				<td width=50%>Result</td>
				<td width=10%>TXT Report</td>
				<td width=10%>Screenshot</td></tr>
		'''		

		html_head  = "<h2>%s</h2>" % name
		html_head += html_table_open
		return html_head

	def _add_results(self, res):

		html_section = '''
		<tr><td>AV_NAME</td>
			<td>AV_KIND</td>
			<td>AV_RESULT</td>
			<td><a href="AV_TXT_LINK">txt report</td>
			<td><a href="AV_SCREEN_LINK"><img src="AV_SCREEN_LINK" width=150 height=150></a></td></tr>
		'''
	
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

	def _add_errors(self, errors):

		html_table_head = '''
		<table border=1 cellpadding=1 cellspacing=2 width=70%>
			<tr><td with=15%>Virtual Machine</td>
				<td with=15%>Kind of test</td>
				<td width=50%>Result</td>
				<td width=10%>TXT Report</td>
				<td width=10%>Screenshot</td></tr>
		'''	

		html_section = '''
		<tr><td>AV_NAME</td>
			<td>AV_KIND</td>
			<td>AV_ERROR</td>
			<td><a href="AV_TXT_LINK">txt report</a></td>
			<td><a href="AV_SCREEN_LINK"><img src="AV_SCREEN_LINK" width=150 height=150></a></td></tr>
		'''

		html_errs = html_table_head
		
		for e in errors:
			html_table = html_section
			html_table = html_table.replace( "AV_NAME", e['av'] )
			html_table = html_table.replace("AV_KIND", e['kind'])
			html_table = html_table.replace( "AV_ERROR", e['result'] )
			html_table = html_table.replace( "AV_TXT_LINK", "results_%s_%s.txt" % (e['av'],e['kind']) )
			html_table = html_table.replace( "AV_SCREEN_LINK", "screenshot_%s_%s.png" % (e['av'],e['kind']) )
			html_errs += html_table
		html_errs += "</table>"

		return html_errs



	def _write_html_report(self, result, html_file_name=None):

		html_table_closed = '</table>'

		content  = ""
		content += "<html><body>"
		content += "<h2>%s</h2>" % datetime.datetime.now()

		if len(result['failed']) > 0:
			content +=  self._add_header("Failed") 
			content +=  self._add_results(result['failed'] )
			content +=  html_table_closed 

		if len(result['errors']) > 0:
			content +=  "<h2>Errors</h2>"
			content +=  self._add_errors(result['errors'])

		if len(result['success']) > 0:
			content +=  self._add_header("Success") 
			content +=  self._add_results(result['success'])
			content +=  html_table_closed 

		content += "</body></html>"

		if html_file_name is None:
			return content
		else:
			f = open(html_file_name, 'wb') 
			f.write(content)
			f.close()

	def _get_results(self):
		errors  = []
		success = []
		failed  = []

		record  = {}
		
		for result in self.results:
			for r in result:
				record = {}
				l = r.split(",")

				if len(l) == 3:
					record['av']     = l[0].strip()
					record['kind']   = l[1].strip()
 					record['result'] = l[2].strip()
					errors.append(record)

				elif len(l) == 4:
					record['av']     = l[0].strip()
					record['kind']   = l[1].strip()
					record['result'] = l[3].replace("\r\n","").replace("+","").strip()

					if "SUCCESS" in record['result']:
						success.append(record)

					elif "FAILED" in record['result']:
						failed.append(record)

		res_list = {} 
		res_list["success"] = success
		res_list["errors"]  = errors
		res_list["failed"]  = failed

		return res_list

	def save_csv(self, csv_file):
		print "Saving csv file with results in %s" % csv_file
		res_list = self._get_results()


	def save_html(self, html_file, on_file=True):
		print "saving in %s" % html_file
		res_list = self._get_results()
		if on_file is True:
			self._write_html_report(res_list, html_file)
		else:
			self._write_html_report(res_list)
	
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


	def _build_mail_body(self, report_file):

		hresults = []
		host = "172.20.20.167"
		port = "8080"

		for av in self.results:
			name = av[0].split(",")[0]
			k = len(av)

			hres = []
			hres.append(name)

			for ares in av:
				r = ares.split(",")
				j = len(r)
				hres.append(r[j-1].strip())

			hresults.append(hres)

		header = "<table><tr><td>AV</td><td>Silent</td><td>Melt</td><td>Exploit</td></tr>"
		line   = "<tr><td>AV_NAME</td><td bgcolor='SCOLOR'>&nbsp;</td><td bgcolor='MCOLOR'>&nbsp;</td><td bgcolor='ECOLOR'>&nbsp;</td></tr>" % ()
		footer = "</table><br><br><b>View full <a href'http://%s:%s/%s'>report</a><b>" % (host, port, report_file)

		content = ""

		with open("/tmp/color.html","wb+") as f:
			content += header

		for res in hresults:
			l = line.replace("AV_NAME",res[0])


			if "SUCCESS" in res[1]:
				l = l.replace("SCOLOR","green")
				print "%s SUCCESS" % res[0]
			elif "FAILED" in res[1]:
				print "%s FAILED" % res[0]
				l = l.replace("SCOLOR","red")
			elif "ERROR" in res[1]:
				print "%s ERROR" % res[0]
				l = l.replace("SCOLOR","black")


			if "SUCCESS" in res[2]:
				l = l.replace("MCOLOR","green")
				print "%s SUCCESS" % res[0]
			elif "FAILED" in res[2]:
				l = l.replace("MCOLOR","red")
				print "%s FAILED" % res[0]
			elif "ERROR" in res[2]:
				l = l.replace("MCOLOR","black")
				print "%s ERROR" % res[0]


			if "SUCCESS" in res[3]:
				l = l.replace("ECOLOR","green")
			elif "FAILED" in res[3]:
				l = l.replace("ECOLOR","red")
			elif "ERROR" in res[3]:
				l = l.replace("ECOLOR","black")

			content += l

		content += footer

		return content


	
	def send_report_color_mail(self, html_file):

		html_file_l = html_file.split("/")[-2:]
		html_file = "%s/%s" % (html_file_l[0],html_file_l[1])
		content = self._build_mail_body(html_file)

		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor Results"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			body = MIMEText(content, 'html')
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False

	def send_report_mail(self):
		if self.report is None: # or os.path.exists(report_link) is False:
			return False

		res_list = self._get_results()

		message = ''

		for error in res_list['errors']:
			print error
			message += "%s, %s, %s\n" % (error['av'],error['kind'],error['result'])
		print "\n\n"

		for fail in res_list['failed']:
			message += "%s, %s, %s\n" % (fail['av'],fail['kind'],fail['result'])
		print "\n\n"

		for success in res_list['success']:
			message += "%s, %s, %s\n" % (success['av'],success['kind'],success['result'])

		try:

			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor Results"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			body = MIMEText(message)
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False
	
	def send_html_mail(self):
		res_list = self._get_results()
		message = self._write_html_report(res_list)

		try:

			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor Results"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			body = MIMEText(message, 'html')
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False



