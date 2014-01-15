from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time


if __name__ == "__main__":
	# path to the directory (relative or absolute)
	dirpath = sys.argv[1] if len(sys.argv) == 2 else r'.'

	# get all entries in the directory w/ stats
	entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
	entries = ((os.stat(path), path) for path in entries)

	# leave only regular files, insert creation date
	entries = ((stat[ST_CTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))

	#NOTE: on Windows `ST_CTIME` is a creation date 
	#  but on Unix it could be something else
	#NOTE: use `ST_MTIME` to sort by a modification date

	for cdate, path in sorted(entries):
	    print time.ctime(cdate), os.path.basename(path)