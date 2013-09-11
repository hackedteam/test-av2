from redis import Redis


def listener(channel="channel", out):

    r = Redis()

    p = r.pubsub()
    p.subscribe(channel)

    for m in r.listen():
        out = m['data']