__author__ = 'zeno'

from AVMaster import report

def test_report_load():
    report.restore("report.STATIC_OSX.log")
    assert report.name == "STATIC_OSX"
    assert report.c_received
    assert report.c_sent


if __name__=="__main__":
    test_report_load()