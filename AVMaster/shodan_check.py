import shodan
import socket;
from multiprocessing import Pool
import smtplib
import time

SHODAN_API_KEY = "zCIv8gkOMF9Oy6hP76VIzTp2ddLzUnTK"

api = shodan.Shodan(SHODAN_API_KEY)


def mail(payload, mail_recipients,  mail_server = "mail.hackingteam.com"):
    # Import the email modules we'll need
    from email.mime.text import MIMEText

    # Create a text/plain message
    for recipient in mail_recipients:
        msg = MIMEText(payload)
        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = 'Report Shodan: %s' % time.asctime()
        msg['From'] = "avtest@hackingteam.com"
        msg['To'] = recipient

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP(mail_server)
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()

def open_port(ip, port=443):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((ip, port))
        sock.close()
    except:
        #print "%s:%s is not open" % (ip, port)
        return False, "%s:%s is not open" % (ip, port)

    #print "%s:%s is open" % (ip, port)
    return True, "%s:%s is open" % (ip, port)


def check_vuln():
    try:

        #print api.services()
        # Search Shodan
        query = '404 notfound json'
        results = api.search(query)

        p = Pool(50)

        # Show the results
        print 'Results found: %s' % results['total']
        ips = [ result['ip_str'] for result in results['matches']]

        print "ips: %s" % ips
        ret = p.map(open_port, ips)
        #print "ret: %s" % ret
        #for result in results['matches']:
        #    ip =result['ip_str']
            #print 'IP: %s %s' % (ip, open_port(ip))
        return ret

    except shodan.APIError, e:
            print 'Error: %s' % e


if __name__ == "__main__":
    ret = check_vuln()

    payload = "Shodan check %s\n" % time.asctime()
    payload += "number of ip scanned: %s\n\n" % len(ret)
    for r,v in ret:
        if r:
            payload += "%s\n" % v

    print payload
    mail(payload, ["zeno@hackingteam.com", "alor@hackingteam.com"])

