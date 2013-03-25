import os

from flask import Flask, render_template

from models import db, app, init_db, Report
from settings import DB_PATH

@app.route('/')
def index_view():
	""" Index page
	Shows list of reports
	"""
	title = "Reports"
	reports = Report.query.all()

	return render_template('index.html', title=title, reports=reports)

@app.route('/view/<r_id>')
def result_view(r_id):
	""" Test Results page
	Show results of spcific scheduled test
	"""
	report = Report.query.filter_by(id=r_id)
	title  = report.date

	results = Result.query.filter_by(report=report)

	return render_template("results.html", title=title, results=results)

if __name__ == "__main__":
	
	init_db(DB_PATH)
	app.run(host='0.0.0.0', port=8000)