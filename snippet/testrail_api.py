import json
import urllib2
from urllib2 import HTTPError
import sys


base_url = "http://172.20.20.168/testrail/"


def send_get(url):
    try:
        req = urllib2.Request(url)
#        req.add_header("Content-type","application/json")
        req.add_header("Accept","application/json")
        f = urllib2.urlopen(req)
        resp = f.read()
    except HTTPError:
        return False
    return resp

def send_post(url,data):
    try:
        req = urllib2.Request(url,data)
        req.add_header("Accept","application/json")
        f = urllib2.urlopen(req)
        resp = f.read()
    except HTTPError:
        return False
    return resp

if __name__ == "__main__":
    print send_get("http://172.20.20.168/")