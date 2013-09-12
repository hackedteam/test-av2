from redis import Redis
channel="channel1"

def client():
    r = Redis()
    p = r.pubsub()
    p.subscribe(channel)
    exit = False
    while not exit:
        for m in p.listen():
            out = m['data']
            print out
            if isinstance(out,str) and "+CMD" in out:
                break
        r.publish(channel, "+SUCCESS result")
        r.publish(channel, "+END result")


def server():
    r = Redis("10.0.20.1")
    p = r.pubsub()
    p.subscribe(channel)
    for cmd in ["START","PUSH","SILENT"]:
        r.publish(channel, "+CMD %s" % cmd)
        for m in p.listen():
            out = m['data']
            print out
            if isinstance(out,str) and "+END" in out:
                break
