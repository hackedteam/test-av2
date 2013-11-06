import sys
from AVAgent.old.puppet import VMachine

from AVAgent.old.puppet.VMManager import VMManagerFus
#from ConsoleAPI import API

if len(sys.argv) < 3:
    sys.stdout.write("[!] ERROR: this is the syntax:\n%s <av name> <ip addr>\n" % sys.argv[0])
    sys.exit(0)

conf_file = "vms.cfg"
vmrun_path = "/Applications/VMwareFusion.app/Contents/Library/vmrun"

# hostname change script paths
host_script_src = "tmp/change_hostname.bat"
host_script_dst = "C:\\Users\\avtest\\Desktop\\change_hostname.bat"

# ip addr of ext if script paths
addr_script_src = "tmp/change_ip_addr.bat"
addr_script_dst = "C:\\Users\\avtest\\Desktop\\change_ip_addr.bat"

# puppet installer path
puppet_path = "C:\\Users\\avtest\\Desktop\\puppet-3.1.0-rc1.msi"

# vSphere creds
host=""
user=""
passwd=""

#
#   Defining VM Manager
#
#vmman = VMManagerVS(vmrun_path, host, user, passwd)
vmman = VMManagerFus(vmrun_path)
#
#   Defining all vms you need
#
avg = VMachine(conf_file, sys.argv[1])

print avg

#
#   Generate scripts for that vm 
#
f = open(addr_script_src, 'wb')
f.write('C:\\Windows\\system32\\netsh.exe interface ip set address "Local Area Connection" static %s 255.255.255.0' % sys.argv[2])
f.close()

g = open(host_script_src, 'wb')
g.write("wmic computersystem where caption='avtagent' rename win7%s" % sys.argv[1])
g.close()

c = raw_input("[>] Ready... Press enter to start")

# 1. startup vm
#vmman.startup(avg)
#
# 2. copy files
vmman.copyFileToGuest(avg, addr_script_src, addr_script_dst)
vmman.copyFileToGuest(avg, host_script_src, host_script_dst)

#
# 3. run scripts
x = vmman.executeCmd(avg, addr_script_dst)
if x is not True:
    sys.stdout.write("[!] error executing %s\n" % addr_script_dst)
    #vmman.shutdown(avg)
    #sys.exit(0)
'''
x = vmman.executeCmd(avg, addr_script_dst)
if x is not True:
    sys.stdout.write("[!] error executing %s\n" % addr_script_dst)
    #vmman.shutdown(avg)
    #sys.exit(0)

#
# 4. wait for reboot
#vmman.reboot(avg)

#
# 5. run puppet installer (maybe issues with UAC)
x = vmman.executeCmd(avg, puppet_path)
if x is not True:
    sys.stdout.write("[!] error executing %s\n" % addr_script_dst)
    #vmman.shutdown(avg)
    #sys.exit(0)
'''