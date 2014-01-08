import json
import urllib2
from urllib2 import HTTPError
import sys
import base64

user_hash = base64.encodestring('apitestrail@hackingteam.com:apicoltore').replace('\n', '')
base_url = "http://172.20.20.168/testrail/index.php?api"

def send_get(url):
    try:
        req = urllib2.Request(url)
#        req.add_header("Content-type","application/json")
        req.add_header("Content-Type","application/json")
        req.add_header("Authorization","Basic %s" % user_hash)
        f = urllib2.urlopen(req).read()
        resp = json.loads(f)
    except HTTPError as e:
        return "HTTPError found: %s" % e
    return resp

def send_post(url,data):
    try:
        req = urllib2.Request(url,data)
        req.add_header("Accept","application/json")
        f = urllib2.urlopen(req)
        resp = f.read()
    except HTTPError:
        return "HTTPError found: %s" % e
    return resp

def get_plans(p_id):
    get_plans_url = "%s/v2/get_plans/%d" % (base_url,p_id)
    return send_get(get_plans_url)

def get_runs(proj_id,plan_id):
    get_runs_url = "%s/v2/get_runs/%d/%s" % (base_url,proj_id,plan_id)
    return send_get(get_runs_url)

def get_plan(proj_id,plan_id):
    for p in get_plans(proj_id):
        if p["id"] == plan_id:
            return p


def main():
    project_id = 1
    plan = get_plan(project_id,55)
    print "%s: %s" % (plan["name"], plan["description"])

    print "Getting Runs for %s" % plan["name"]
    print get_runs(project_id, plan["id"])

if __name__ == "__main__":
    main()