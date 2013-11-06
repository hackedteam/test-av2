from AVAgent.old.puppet import Analysis

from ConsoleAPI import API

vms_conf_file = "vms.cfg"
analysis_conf_file = "analysis.cfg"

exe_path_src = "/Users/olli/Documents/work/AVTesting/malware/arg.exe"
exe_path_dst = "c:\\Users\\avtest\\Desktop\\arg.exe"



analysis = Analysis(analysis_conf_file)
analysis.start()