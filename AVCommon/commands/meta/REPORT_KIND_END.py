__author__ = 'zeno'

import time
from AVCommon.logger import logging
from AVCommon import command

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
        run_name = report_args.pop(0)
        test_case = report_args.pop(0)

        proj_id = 1
        plan_name = "Continuous Testing"

        if success and not "INVERT" in report_args:
            result = 'passed'
        else:
            result = 'failed'

        configs={ 'AV Invisibility': "%s, Windows" % vm}

        config = configs.get(run_name, vm)


        plan = testrail_api.get_plan(proj_id, plan_name=plan_name)
        plan_id = plan["id"]

        testrail_api.add_plan_result(proj_id, plan_id, config, run_name, test_case, result, int(elapsed))

    except:
        logging.exception("error testrail")

    return success, "%s| %s" % (vm, proc_name)
