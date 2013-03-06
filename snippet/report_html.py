import os
import sys


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


def parse_results(filename):

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
						'''
						res['av'] = j[0][:-1]
						res['kind'] = j[1]
						'''
						res['av'] = j[1]
						res['kind'] = j[0]
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

def add_header(name):
	html_head  = "<h2>%s</h2>" % name
	html_head += html_table_open
	return html_head

def add_results(res):
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

def add_errors(errors):
	html_errs = ""
	for e in errors:
		html_errs += e
	return html_errs



def write_html_report(results, html_file_name):
	success,errors,failed = results

	with open(html_file_name, 'wb') as f:
		f.write("<html><body>")

		f.write( add_header("Failed") )
		f.write( add_results(failed) )
		f.write( html_table_closed)

		f.write( "<h2>Errors</h2>")
		f.write( add_errors(errors) )

		f.write( add_header("Success") )
		f.write( add_results(success) )
		f.write( html_table_closed)

		f.write("</body></html>")
		



if __name__ == "__main__":
	html_file_name = "/tmp/bozz.html"
	results = parse_results("/tmp/bozz")

	write_html_report(results, html_file_name)





