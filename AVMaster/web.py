import os

from flask import Flask, render_template

from lib.web.models import db, app, init_db, Test, Result
from lib.web.settings import DB_PATH

@app.route('/')
def index_view():
	""" Index page
	Shows list of reports
	"""
	title = "Reports"
	reports = Test.query.all()

	return render_template('index.html', title=title, reports=reports)

@app.route('/view/<t_id>')
def result_view(t_id):
	""" Test Results page
	Show results of spcific scheduled test
	"""
	report = Test.query.filter_by(id=t_id).first_or_404()
	title  = report.time

	results = Result.query.filter_by(test_id=report.id)

	if not results:
		results = None

	return render_template("results.html", title=title, results=results)

if __name__ == "__main__":
	
	init_db(DB_PATH)
	app.run(host='0.0.0.0', port=8000)