DB_PATH="../share/avmonitor.db"
DEBUG=True
SQLALCHEMY_DATABASE_URI='sqlite:///%s' % DB_PATH
SECRET_KEY='development-key'
CSRF_ENABLED=True