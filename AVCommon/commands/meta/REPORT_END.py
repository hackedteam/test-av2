__author__ = 'zeno'


from AVCommon import command
import logging

def execute(vm, args):
    # counts the end, when it's equal to init, finish
    from AVMaster import report

    logging.debug("    CS REPORT_KIND: %s,%s" % (vm,args))
    protocol, args = args
    assert "report" in command.context.keys()
    assert vm in command.context["report"]

    command.context["report"].remove(vm)
    #if not command.context["report"]:
    #    logging.info("report end: %s" % vm)
    report.end(vm)
    if not command.context["report"]:
        report.finish()

    logging.debug("    CS Execute")
    return True, vm