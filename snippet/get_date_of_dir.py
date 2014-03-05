from stat import S_ISREG, S_ISDIR, ST_CTIME, ST_MODE
from socket import gethostname
import os, sys, time

dir = {}

dir['avast']  = ( "C:\\Program Files\\AVAST Software\\Avast", "defs" ) # OK
dir['comodo'] = ( "C:\\ProgramData\\COMODO\\Cis\\cmc2", "local_trees" ) # OK
dir['kis14']    = ( "C:\\ProgramData\\Kaspersky Lab\\AVP14.0.0\\Data", "updater" ) # IT WORKS
dir['mcafee'] = ( "C:\\ProgramData\McAfee\\MSC\\Updates", "Download" ) # OK
dir['norton'] = ( "C:\\Program Files (x86)\\Norton Internet Security\\NortonData\\21.1.0.18\\Definitions", "VirusDefs" ) #OK
dir['panda']  = ( "C:\\Program Files (x86)\\Panda Security\\Panda Internet Security 2013", "Downloads" ) # OK

dir['avg']    = ( "C:\\ProgramData\\AVG2013\\IDS", "malwareprofile" )            # WRONG DIRECTORY
dir['avira']  = ( "C:\\ProgramData\\Avira\\AntiVir Desktop", "UPDATE" ) # WRONG DIR


def get_date_from_dir(dirpath, pname):
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)

    entries = ((stat[ST_CTIME], path) for stat, path in entries if pname in path) #S_ISDIR(stat[ST_MODE]) and pname in path)

    #NOTE: use `ST_MTIME` to sort by a modification date

    for cdate, path in sorted(entries):
        print time.ctime(os.path.getmtime(path)), os.path.basename(path)

if __name__ == "__main__":

    # get your av name
    av = gethostname()

    if "winxp" in av:
        av = av.replace("winxp","")
    elif "win7" in av:
        av = av.replace("win7","")
    else: # "win8" in av:
        av = av.replace("win8","")

    #then check for date on the associated file
    try:
        get_date_from_dir(dir[av][0],dir[av][1])
    except KeyError:
        print "key %s not found" % av

