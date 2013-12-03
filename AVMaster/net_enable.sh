shorewall restart /etc/shorewall-nat-enabled/ > networking_log.txt

#/sbin/iptables -t nat -A PREROUTING -p tcp -s 10.0.20.0/24 -d $1 --dport 80 -j LOG --log-prefix "[RCS-SYNC]"
/sbin/iptables -t nat -A PREROUTING -p tcp -s 10.0.20.0/24 -d 172.20.100.204 --dport 80 -j DNAT --to-destination 192.168.100.204:80

if [ -e "/var/log/rcs.log" ]; then
	rm /var/log/rcs.log
fi

if [ -e "/var/log/detected" ]; then
	rm /var/log/detected
fi