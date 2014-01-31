import json
import urllib2
from urllib2 import HTTPError
import sys
import base64
import pprint

from AVCommon.logger import logging

user_hash = base64.encodestring('apitestrail@hackingteam.com:apicoltore').replace('\n', '')
base_url = "http://172.20.20.168/testrail/index.php?/api"

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

def get_statuses():
    get_url = "%s/v2/get_statuses" % (base_url)
    return send_get(get_url)

def get_case(case_id):
    get_url = "%s/v2/get_case/%d" % (base_url,case_id)
    return send_get(get_url)

def get_plans(p_id):
    get_plans_url = "%s/v2/get_plans/%s" % (base_url,p_id)
    return send_get(get_plans_url)

def _get_plan(plan_id):
    get_plans_url = "%s/v2/get_plan/%s" % (base_url,plan_id)
    return send_get(get_plans_url)

def get_runs(proj_id, plan_id):
    get_runs_url = "%s/v2/get_runs/%s" % (base_url,proj_id)
    runs = send_get(get_runs_url)
    return [ r for r in runs if r["plan_id"] == plan_id ]

def get_tests(run_id):
    get_tests_url = "%s/v2/get_tests/%d" % (base_url, run_id)
    return send_get(get_tests_url)

def search_plan(proj_id, plan_id=-1, plan_name=""):
    for p in get_plans(proj_id):
        if p["is_completed"]:
            continue
        if p["id"] == plan_id or p["name"] == plan_name:
            return _get_plan(p["id"])

def get_run(proj_id, plan_id, run_id=-1, run_name=""):
    for r in get_runs(proj_id, plan_id):
        if r["id"] == run_id or r["name"] == run_name:
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

def add_result(test_id, result, comment="", elapsed=0, defects="", version=0 ):

    res = { "status_id": result,
            "elapsed": elapsed,
            "comment": comment }
    add_result_url = "%s/v2/add_result/%d" % (base_url, test_id)
    return send_post(add_result_url, res)

def rerun_plan(project_id,plan_id):
    plan = search_plan(project_id, plan_id)
    runs =  get_runs(project_id, plan_id)

    for r in runs:
        pprint.pprint(r)
        break
    #return

    new_plan = {}
    new_plan["name"] = plan["name"] + " AUTO re-config"
    #new_plan["entries"] = runs
    new_plan["description"] = "automatic plan"
    new_plan["milestone_id"] = plan["milestone_id"]
    new_plan_ret = add_plan(project_id, new_plan)

    new_plan_id = new_plan_ret["id"]
    print new_plan_id
    for r in runs:
        r["name"] = "%s [%s]" % (r["name"], r["config"])
        add_plan_entry(new_plan_id, r)

    #close_plan(plan_id)
    return new_plan_id

def add_plan_result(proj_id, plan_id, config, run_name, test_case, result, elapsed = 0, comment="avg"):
    logging.debug("adding plan result: %s, %s, %s, %s, %s" % (config, run_name, test_case, result, comment))
    statuses = get_statuses()

    results = dict([ (s['name'],s['id']) for s in statuses])

    plan = search_plan(proj_id, plan_id)

    entries = plan["entries"]
    for entry in entries:
        runs = entry["runs"]
        for r in runs:
            if r["name"] != run_name:
                continue
            logging.debug("run: %s" % r)
            #pprint.pprint(r)
            #break

            if r["config"] != config:
                continue

            for t in get_tests(r["id"]):
                if test_case in t["title"]:
                    logging.debug("adding result for test: %s" % t["id"])
                    add_result(t["id"], results[result], comment, elapsed)
                    return r["id"]
    logging.error("cannot find correct test case")

def main():
    proj_id = 1
    plan_name = "Continuous Testing"
    run_name = "AV Invisibility"
    test_case = "Soldier"
    #test_case_id = 1
    result = "retest"
    config = "360cn5, Windows"

    #plan_id = 55
    #plan = get_plan(project_id, plan_id)
    plan = search_plan(proj_id, plan_name=plan_name)
    plan_id = plan["id"]

    add_plan_result(proj_id, plan_id, config, run_name, test_case, result, 60.1)

    #new_plan_id = rerun_plan(project_id, plan_id)


if __name__ == "__main__":
    main()