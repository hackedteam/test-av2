import os

ROOT_DIR=os.getcwd()
DB_PATH="%s/data/avmonitor.db" % ROOT_DIR
#DB_PATH="avmonitor"
DEBUG=True
SQLALCHEMY_DATABASE_URI='sqlite:///%s' % DB_PATH
#SQLALCHEMY_DATABASE_URI='mysql://avmonitor:avmonitorp123@localhost/%s' % DB_PATH
SECRET_KEY='development-key'
CSRF_ENABLED=True