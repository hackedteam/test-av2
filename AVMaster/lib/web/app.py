import sys
import os

from base64 import b64encode
from flask import render_template, Response
from sqlalchemy import desc

from lib.web.models import app, Test, Result, Sample, init_db
#from lib.web.db import init_db
from lib.web.settings import DB_PATH


@app.route('/')
def index_view():
    """ Index page
    Shows list of reports
    """
    title = "Reports"
    reports = Test.query.order_by(desc(Test.id))

    return render_template('index.html', title=title, reports=reports)


@app.route('/report/<t_id>/result/<name>/<kind>')
def result_view(t_id, name, kind):
    """ Test Result page
    Show results of scheduled test on spcific virtual machine
    """
    test = Test.query.filter_by(id=t_id).first_or_404()
    result = Result.query.filter_by(
        test_id=t_id, vm_name=name, kind=kind).first_or_404()

    if not result:
        result = None
    else:
        result.result = result.result.split(", ")
        if result.log is not None:
            result.log = result.log.split(", ")
        if result.scrshot is not None:
            result.scrshot = b64encode(result.scrshot)

        sample = Sample.query.filter_by(r_id=result.id)
        if not sample:
            sample = None

    return render_template("result.html", title=test.time, result=result, sample=sample)


@app.route('/report/<t_id>/result/<name>/<kind>/image')
def image_view(t_id, name, kind):
    result = Result.query.filter_by(
        test_id=t_id, vm_name=name, kind=kind).first_or_404()

    if not result.scrshot:
        screenshot = None
    else:
        screenshot = b64encode(result.scrshot)

    return render_template("image.html", t_id=t_id, screenshot=screenshot)


@app.route('/report/<t_id>/result/<name>/<kind>/sample')
def sample_view(t_id, name, kind):
    result = Result.query.filter_by(
        test_id=t_id, vm_name=name, kind=kind).first_or_404()
    sample = Sample.query.filter_by(r_id=result.id).first()

    return Response(sample.exe, mimetype="application/zip",
                    headers={"Content-Disposition": "attachment;filename=build.zip"})


@app.route('/results/<t_id>')
def results_view(t_id):
    test = Test.query.filter_by(id=t_id).first_or_404()
    results = Result.query.filter_by(test_id=t_id).order_by(Result.vm_name)
    return render_template("results.html", test=test, results=results)


@app.route('/report/<t_id>')
def report_view(t_id):
    """ Report page
    Show report page
    """
    test = Test.query.filter_by(id=t_id).first_or_404()
    title = test.time

    results = Result.query.filter_by(test_id=test.id).order_by(Result.vm_name)

    av_list = []
    hcolumns = [u'name']

    hresults = []
    hres = {}

    for res in results:
        if res.vm_name not in av_list:
            av_list.append(res.vm_name)
        if res.kind not in hcolumns:
            hcolumns.append(res.kind)
        hres['name'] = res.vm_name
        hres[res.kind] = res.result
        hresults.append(hres)

    print "hcolumns: %s" % hcolumns
    print "av_list: %s" % av_list

    reports = []

    for av in av_list:
        res = Result.query.filter_by(vm_name=av, test_id=test.id)
        report = {}
        report['name'] = av
        report['t_id'] = test.id
        report['results'] = {}

        for r in res:
            if "END" in r.result.split(", ")[-1]:
                report['results'][r.kind] = [r.kind, r.result.split(", ")[-2]]
            else:
                report['results'][r.kind] = [r.kind, r.result.split(", ")[-1]]

        print report
        reports.append(report)

    return render_template("report.html", title=title, av_list=av_list, hcolumns=hcolumns, reports=reports)

if __name__ == "__main__":
    port = 8000

    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    init_db(DB_PATH)
    app.run(host='0.0.0.0', port=port)
