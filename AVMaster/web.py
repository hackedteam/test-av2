import os

from flask import Flask, render_template

from lib.web.models import db, app, init_db, Test, Result, Report
from lib.web.settings import DB_PATH

@app.route('/')
def index_view():
	""" Index page
	Shows list of reports
	"""
	title = "Reports"
	reports = Test.query.all()

	return render_template('index.html', title=title, reports=reports)

@app.route('/result/<t_id>')
def result_view(t_id):
	""" Test Results page
	Show results of spcific scheduled test
	"""
	test = Test.query.filter_by(id=t_id).first_or_404()
	title  = test.time

	results = Result.query.filter_by(test_id=test.id)

	if not results:
		results = None

	return render_template("results.html", title=title, results=results)

@app.route('/report/<t_id>')
def report_view(t_id):
	test = Test.query.filter_by(id=t_id).first_or_404()
	title  = test.time

	results = Result.query.filter_by(test_id=test.id).order_by(Result.vm_name)

	av_list = []
	hcolumns = [ u'name' ]

	hresults = []
	hres = {}

	for res in results:
		if res.vm_name not in av_list:
			av_list.append(res.vm_name)
		if res.kind not in hcolumns:
			hcolumns.append(res.kind)
		hres['name'] = res.vm_name
		hres[res.kind] = res.result
		hresults.append(hres)

	print "hcolumns: %s" % hcolumns
	print "av_list: %s" % av_list

	reports = []

	for av in av_list:
		report = {}
		report['name'] = av
		report['results'] = {}
		j=0
		for i in range( 0, (len(hcolumns) - 1) ):
			report['results'][hcolumns[i+1]] = results[j+i].result.split(", ")[-1]
		j += len(hcolumns) - 1
		#report['results'] = sort(report['results'])
		reports.append(report)
		print report

	return render_template("report.html", title=title, av_list=av_list, hcolumns=hcolumns, reports=reports)

if __name__ == "__main__":
	
	init_db(DB_PATH)
	app.run(host='0.0.0.0', port=8000)