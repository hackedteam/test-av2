results=[]
results.append(["emsisoft, silent, ERROR saving results with exception: [Errno 2] No such file or directory: 'repp/dispatch_20130307_0939/results_emsisoft_silent.txt'","emsisoft, melt, ERROR saving results with exception: [Errno 2] No such file or directory: 'repp/dispatch_20130307_0939/results_emsisoft_silent.txt'","emsisoft, exploit, ERROR saving results with exception: [Errno 2] No such file or directory: 'repp/dispatch_20130307_0939/results_emsisoft_silent.txt'"])
results.append(['norton, silent, 2013-03-07 11:26:45, INFO: + SUCCESS ELITE UNINSTALLED\r\n','norton, melt, 2013-03-07 11:26:45, INFO: + SUCCESS ELITE UNINSTALLED\r\n','norton, exploit, 2013-03-07 11:26:45, INFO: + SUCCESS ELITE UNINSTALLED\r\n'])
results.append(['mcafee, silent, 2013-03-07 11:00:04, INFO: + FAILED SCOUT SYNC\r\n','mcafee, melt, 2013-03-07 11:00:04, INFO: + FAILED SCOUT SYNC\r\n','mcafee, exploit, 2013-03-07 11:00:04, INFO: + FAILED SCOUT SYNC\r\n'])

hresults = []


def build_mail_body(results):

    for av in results:
        name = av[0].split(",")[0]
        k = len(av)

        hres = []
        hres.append(name)

        for ares in av:
            r = ares.split(",")
            j = len(r)
            hres.append(r[j-1].strip())

        hresults.append(hres)


    header = "<table><tr><td>AV</td><td>Silent</td><td>Melt</td><td>Exploit</td></tr>"
    line   = "<tr><td>AV_NAME</td><td bgcolor='SCOLOR'><a href='#' class='fill-div'></td><td bgcolor='MCOLOR'><a href='#' class='fill-div'></td><td bgcolor='ECOLOR'><a href='#' class='fill-div'></td></tr>"
    footer = "</table>"

    content = ""


    with open("/tmp/color.html","wb+") as f:
        content += header

    for res in hresults:
        l = line.replace("AV_NAME",res[0])


        if "SUCCESS" in res[1]:
            l = l.replace("SCOLOR","green")
            print "%s SUCCESS" % res[0]
        elif "FAILED" in res[1]:
            print "%s FAILED" % res[0]
            l = l.replace("SCOLOR","red")
        elif "ERROR" in res[1]:
            print "%s ERROR" % res[0]
            l = l.replace("SCOLOR","black")


        if "SUCCESS" in res[2]:
            l = l.replace("MCOLOR","green")
            print "%s SUCCESS" % res[0]
        elif "FAILED" in res[2]:
            l = l.replace("MCOLOR","red")
            print "%s FAILED" % res[0]
        elif "ERROR" in res[2]:
            l = l.replace("MCOLOR","black")
            print "%s ERROR" % res[0]


        if "SUCCESS" in res[3]:
            l = l.replace("ECOLOR","green")
        elif "FAILED" in res[3]:
            l = l.replace("ECOLOR","red")
        elif "ERROR" in res[3]:
            l = l.replace("ECOLOR","black")

        content += l

    content += footer

