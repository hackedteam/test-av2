import os

from datetime import datetime
from flask import Flask, request, render_template, flash, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy

#import jinja2

app = Flask(__name__)
app.config.from_pyfile('settings.py')
#app.jinja_env.undefined = jinja2.StrictUndefined
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
	id      = db.Column(db.Integer, primary_key=True)
	vm_name = db.Column(db.String(16))
	test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
	kind    = db.Column(db.String(16))
	result  = db.Column(db.Text)
	scrshot = db.Column(db.BLOB)
	log     = db.Column(db.Text)

	def __init__(self, vm_name, test_id, kind, status, result=None):
		self.kind    = kind
		self.status  = status
		self.vm_name = vm_name
		self.test_id = test_id
		
		if result is not None:
			self.result = result

class Sample(db.Model):
	id   = db.Column(db.Integer, primary_key=True)
	r_id = db.Column(db.Integer, db.ForeignKey('result.id'))
	exe  = db.Column(db.BLOB)

	def __init__(self, r_id, exe):
		self.r_id = r_id
		self.exe  = exe 

def init_db(db_path):
	""" If no db found create one """
	if not os.path.exists(db_path):
		print "[!] No database found! Creating one"
		db.create_all()

#if __name__ == "__main__":
	#init_db()
	#assert Report(0,"22-12-22-03:03:03") not None
	#assert Result("melt","SUCCESS","SUCCES SYNC") not None
