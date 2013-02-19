echo Running > c:\Users\avtest\Desktop\routedns.txt
c:\Users\avtest\Desktop\elevate.exe -c c:\windows\system32\route.exe -p DELETE 192.168.200.0 MASK 255.255.255.0 192.168.100.1
c:\Users\avtest\Desktop\elevate.exe c:\Windows\system32\netsh.exe interface ip set dns name="Local Area Connection 2" static None