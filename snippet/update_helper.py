from stat import S_ISREG, S_ISDIR, ST_CTIME, ST_MODE
from socket import gethostname
import os, sys, time


class UpdateHelper():
    updir = {}
    updir['avast']  = ( "C:\\Program Files\\AVAST Software\\Avast", "defs" )
    updir['avg']    = ( "C:\\ProgramData\\AVG2014", "DB" )
    updir['avira']  = ( "C:\\ProgramData\\Avira\\AntiVir Desktop", "UPDATE" )
    updir['comodo'] = ( "C:\\ProgramData\\COMODO\\Cis\\cmc2", "local_trees" )
    updir['kav']    = ( "C:\ProgramData\Kaspersky Lab\AVP14.0.0\Data\updater\supd_b90b2edf", "updater.xml" )
    updir['mcafee'] = ( "C:\\ProgramData\McAfee\\MSC\\Updates", "Download" )
    updir['norton'] = ( "C:\\Program Files (x86)\\Norton Internet Security\\NortonData", "21.1.0.18" )
    updir['panda']  = ( "C:\\Program Files (x86)\\Panda Security\\Panda Antivirus Pro 2014", "Downloads" )

    def __init__(self, vm_name):
        self.av = vm_name

    def getUpdateDate(self):
        update = {}
        entries = (os.path.join(self.updir[self.av][0], fn))
        entries = (os.path.join(self.updir[self.av][0], fn) for fn in os.listdir(self.updir[self.av][0]))
        entries = ((os.stat(path), path) for path in entries)
        entries = ((stat[ST_CTIME], path) for stat, path in entries if self.updir[self.av][1] in path)

        for cdate, path in sorted(entries):
            print time.ctime(cdate), os.path.basename(path)
            update["time"] = time.ctime(cdate)
            update["file"] = os.path.basename(path)
        return update

    def forceUpdate(self):
        print "forcing update!"

if __name__ == "__main__":

    # get your av name
    av = gethostname()

    if "winxp" in av:
        av = av.replace("winxp","")
    elif "win7" in av:
        av = av.replace("win7","")
    else: # "win8" in av:
        av = av.replace("win8","")

    u = UpdateHelper(av)
#    v = UpdateHelper("avast")

    #then check for date on the associated file
    try:
        u.getUpdateDate()
#        v.getUpdateDate()
    except KeyError as ke:
        print "Antivirus %s not found" % ke

