import os

from flask import Flask, render_template

from models import db, app, init_db, Report

@app.route('/')
def index_view():

	title = "Reports"
	reports = Report.query.all()

	return render_template('index.html', title=title, reports=reports)

@app.route('/view/<r_id>')
def result_view(r_id):

	return render_template("results.html", title=title, results=results)

if __name__ == "__main__":
	#if not os.path.exists("avmonitor.db"):
	#	init_db()
	#app.run(host='172.20.20.167', port=8000)
	app.run(host='0.0.0.0', port=8000)