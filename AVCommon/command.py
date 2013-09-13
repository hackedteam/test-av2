from communicator import CommunicatorRedisList

class Command:
    def __init__(self, frm=None, to=None, host="localhost"):
        if frm is not None:
            self.receive = CommunicatorRedisList(host, frm)
        if to is not None:
            self.send = CommunicatorRedisList(host, to)

    def send(self, cmd):
        self.send.write([frm,cmd])

    def receive(self):
        received = self.receive.read()
        return received
