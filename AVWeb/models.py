import os

from datetime import datetime
from flask import Flask, request, render_template, flash, url_for, \
    redirect
#from flaskext import wtf
#from flaskext.wtf import validators

app = Flask(__name__)
app.config.from_pyfile('settings.py')
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class Report(db.Model):
	id     = db.Column(db.Integer, primary_key=True)
	time   = db.Column(db.Date)
	status = db.Column(db.String(10))

	def __init__(self, type):
		self.type = type
		self.time = datetime.now()

class Result(db.Model):
	id        = db.Column(db.Integer, primary_key=True)
	report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
	kind      = db.Column(db.String(10))
	res_short = db.Column(db.String(50))
	res_full  = db.Column(db.Text)

	def __init__(self, kind, res_short, res_full):
		self.kind      = kind
		self.result    = result
		self.res_short = res_short
		self.res_full  = res_full

def init_db():
	""" If no db found create one """
	if not os.path.exists("avmonitor.db"):
		print "[!] No database found! Creating one"
		db.create_all()
