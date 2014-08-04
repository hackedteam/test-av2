import os

from datetime import datetime
from flask import Flask, request, render_template, flash, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy

#import jinja2

app = Flask(__name__)
app.config.from_pyfile('settings.py')
#app.jinja_env.undefined = jinja2.StrictUndefined
db = SQLAlchemy(app)

""" Test class
    definisce un'esecuzione di un determinato test
"""
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)                        # test id
    #time   = db.Column(db.DateTime)
    time = db.Column(db.String(25))                                     # start time
    status = db.Column(db.Integer)  # 0: started, 1: completed          # status of test
    results = db.relationship('Result', backref='test', lazy='dynamic') # results

    def __init__(self, status, time):
        self.status = status
        self.time = time

""" Test Result
    definisce uno dei risultati del test (es avira, melt, SUCCESS)
"""
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)                          # result id
    vm_name = db.Column(db.String(16), index=True)                        # vm where test is executed
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), index=True) # test id referenced
    kind = db.Column(db.String(16)) # silent, melt, exploit...            # kind of test
    result = db.Column(db.Text)                                           # result
    scrshot = db.Column(db.BLOB)                                          # binary of screenshot
    log = db.Column(db.Text)                                              # logs

    def __init__(self, vm_name, test_id, kind, status, result=None):
        self.kind = kind
        self.status = status
        self.vm_name = vm_name
        self.test_id = test_id

        if result is not None:
            self.result = result

""" Sample
    definisce un Sample. viene salvato il sample quando il test viene completato come FAILED
"""
class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)             # sample id
    r_id = db.Column(db.Integer, db.ForeignKey('result.id')) # result referenced
    exe = db.Column(db.BLOB)                                 # exe blob

    def __init__(self, r_id, exe):
        self.r_id = r_id
        self.exe = exe

""" init db if db doesnt exists """
def init_db(db_path):
    """ If no db found create one """
    if not os.path.exists(db_path):
        print "[!] No database found! Creating one"
        db.create_all()

    # if __name__ == "__main__":
    # init_db()
    # assert Report(0,"22-12-22-03:03:03") not None
    # assert Result("melt","SUCCESS","SUCCES SYNC") not None
