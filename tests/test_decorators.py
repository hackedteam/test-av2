import sys

sys.path.append("../AVCommon")

from AVCommon.decorators import *


class testingDecorators():
    @ignore
    def myFunction(self):
        print "hello world"  # pragma: no cover

    @report
    def execute(self):
        print "executing"

    @returns(int)
    def id(self, v):
        return v


def test_decorators():
    t = testingDecorators()
    print "CALL"
    t.myFunction()
    print "END"

    t.execute()

    print t.id(1)
    try:
        print t.id("hello")
        assert not "Should not be here"
    except:
        pass


if __name__ == '__main__':
    test_decorators()
