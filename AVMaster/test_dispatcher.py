from vmManager import *

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Protocol
from AVCommon import MQ


def test_dispatcher()


    v = vmManager()
    host = "localhost"

    clients = ["kis", "mcafee"]

    update = Procedure("UPDATE", [ "REVERT", "STARTVM", "UPDATE", "STOPVM" ] )
    update = Procedure("UPDATE", [ , "STARTVM", "UPDATE", "STOPVM" ] )


    dispatch = Procedure("DISPATCH", [ "REVERT", "STARTVM", "STARTAGENT" ] )
    scout = Procedure("SCOUT", [ "PROCEDURE(dispatch)", ])



    d = dispatcher()
