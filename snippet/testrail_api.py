import json
import urllib2
from urllib2 import HTTPError
import sys
import base64
import pprint

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

def send_post(url, data):
    try:
        req = urllib2.Request(url,json.dumps(data))
        req.add_header("Content-Type","application/json")
        req.add_header("Authorization","Basic %s" % user_hash)
        f = urllib2.urlopen(req).read()
        resp = json.loads(f)
    except HTTPError as e:
        return "HTTPError found: %s" % e
    return resp

def get_plans(p_id):
    get_plans_url = "%s/v2/get_plans/%d" % (base_url,p_id)
    return send_get(get_plans_url)

def get_runs(proj_id,plan_id):
    get_runs_url = "%s/v2/get_runs/%d/%s" % (base_url,proj_id,plan_id)
    return send_get(get_runs_url)

def get_tests(run_id):
    get_tests_url = "%s/v2/get_tests/%d" % (base_url, run_id)
    return send_get(get_tests_url)

def get_plan(proj_id,plan_id):
    for p in get_plans(proj_id):
        if p["id"] == plan_id:
            return p

def get_run(proj_id, plan_id, r_id):
    for r in get_runs(proj_id, plan_id):
        if r["id"] == r_id:
            return r

def get_results(t_id):
    get_results_url = "%s/v2/get_results/%d" % (base_url, t_id)
    return send_get(get_results_url)

def add_plan(project_id, plan):
    add_plan_url = "%s/v2/add_plan/%d" % (base_url, project_id)
    return send_post(add_plan_url, plan)

def add_plan_entry(plan_id, plan_entry):
    add_plan_url = "%s/v2/add_plan_entry/%d" % (base_url, plan_id)
    return send_post(add_plan_url, plan_entry)

def add_result(test_id, result):
    add_result_url = "%s/v2/add_result/%d" % (base_url, test_id)
    return send_post(add_result_url, result)

def rerun_plan(project_id,plan_id):
    plan = get_plan(project_id, plan_id)
    runs =  get_runs(project_id, plan_id)

    new_plan = {}
    new_plan["name"] = plan["name"] + " AUTO"
    #new_plan["entries"] = runs
    new_plan["description"] = "automatic plan"
    new_plan["milestone_id"] = plan["milestone_id"]
    new_plan_ret = add_plan(project_id, new_plan)

    new_plan_id = new_plan_ret["id"]
    print new_plan_id
    for r in runs:
        add_plan_entry(new_plan_id, r)

    #close_plan(plan_id)
    return new_plan_id

def main():
    project_id = 1
    plan_id = 55
    plan = get_plan(project_id, plan_id)
    '''
    #print  "%s: %s" % (plan["name"], plan["description"])
    #pprint.pprint(plan)
    #return
    #pprint.pprint( get_runs(project_id, plan["id"]))
    #run = get_run(project_id, plan["id"], 275)
    #pprint.pprint(run)
    print "Getting Runs for %s (%s)" % (plan["name"], plan["id"])
    runs =  get_runs(project_id, plan["id"])
    #pprint.pprint(runs)
    for r in runs:
        if r["config"]== "avg":
            #pprint.pprint(r)
            for t in get_tests(r["id"]):
                if "Update" in  t["title"]:
                    print "Searching stuff for AVG"
                    #r = get_results(t["id"])
                    res = {"status_id": "4"}
                    #add_result(t["id"],res)
                    #r = get_results(t["id"])
                    #print t["title"], r[0]["status_id"]
#            pprint.pprint(  )

            print "---"
    '''
    new_plan_id = rerun_plan(project_id, plan_id)


if __name__ == "__main__":
    main()