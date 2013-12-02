__author__ = 'zeno'

from AVMaster import report

def test_report_load():
    r = report.restore("report.TEST_DAILY.log")

    r2 = report.Report()
    assert r.c_sent == r2.c_sent

    assert r.name == "TEST_DAILY"
    assert r.c_received
    assert r.c_sent


if __name__=="__main__":
    test_report_load()