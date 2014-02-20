__author__ = 'zeno'

import time
from AVCommon.logger import logging
from AVCommon import helper

def execute(vm, protocol, args):
    # change the kind for the vm
    from AVMaster import report
    from AVMaster import testrail_api

    proc_name, report_args = args

    logging.debug("    CS REPORT_KIND_END:  %s, %s, %s" % (vm, proc_name, report_args))
    #assert vm in command.context["report"], "report: %s" % command.context["report"]

    success = not protocol.error
    logging.debug("%s, success: %s" % (vm, success))

    elapsed = (time.time() - protocol.elapsed) / 60

    try:
        # ['AV Invisibility', 'Melt']
        # ['AV Invisibility', 'Melt', INVERT]

        if report_args:
            run_name = report_args.pop(0)
            test_case = report_args.pop(0)

            proj_id = 1

            hostname = helper.get_hostname()

            plan_name = "Continuous Testing %s" % hostname

            if  "INVERT" in report_args:
                result = 'failed' if success else 'passed'
            else:
                result = 'passed' if success else 'failed'

            configs={ 'AV Invisibility': "%s, Windows" % vm, 'AV Invisibility Static': "%s, Windows" % vm}

            config = configs.get(run_name, vm)

            logging.debug("search plan %s on %s" % (proj_id, plan_name))
            plan = testrail_api.search_plan(proj_id, plan_name=plan_name)
            plan_id = plan["id"]

            errors = "\n".join(protocol.errors)
            testrail_api.add_plan_result(proj_id, plan_id, config, run_name, test_case, result, int(elapsed), errors)

    except:
        logging.exception("error testrail")

    return success, "%s| %s" % (vm, proc_name)
