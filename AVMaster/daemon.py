import sys

from lib.web.app import DB_PATH, init_db, app

def init_web():
	port = 8000

	if len(sys.argv) == 2:
		port = int(sys.argv[1]) 

	init_db(DB_PATH)

	app.run(host='0.0.0.0', port=port)

def main():

	init_web()

if __name__ == "__main__":
	main()