import os

from datetime import datetime
from flask import Flask, request, render_template, flash, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)

class Test(db.Model):
	id      = db.Column(db.Integer, primary_key=True)
	#time   = db.Column(db.DateTime)
	time    = db.Column(db.String(25))
	status  = db.Column(db.Integer) # 0: started, 1: completed
	results = db.relationship('Result', backref='test', lazy='dynamic')

	def __init__(self, status, time):
		self.status = status
		self.time   = time

class Result(db.Model):
	id        = db.Column(db.Integer, primary_key=True)
	vm_name   = db.Column(db.String(15))
	test_id   = db.Column(db.Integer, db.ForeignKey('test.id'))
	kind      = db.Column(db.String(10))
	res_short = db.Column(db.String(50))
	res_full  = db.Column(db.Text)
	status    = db.Column(db.Integer) # 0: ADDED, 1: STARTED 2: RUNNING 3: COMPLETED

	def __init__(self, kind, res_short, res_full):
		self.kind      = kind
		self.result    = result
		self.res_short = res_short
		self.res_full  = res_full

def init_db(db_path):
	""" If no db found create one """
	if not os.path.exists(db_path):
		print "[!] No database found! Creating one"
		db.create_all()

#if __name__ == "__main__":
	#init_db()
	#assert Report(0,"22-12-22-03:03:03") not None
	#assert Result("melt","SUCCESS","SUCCES SYNC") not None
