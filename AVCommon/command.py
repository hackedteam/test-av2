from communicator import CommunicatorRedisList

class Command:
    def __init__(self, frm=None, to=None, host="localhost"):
        self.frm = frm
        if frm is not None:
            self.receive_from = CommunicatorRedisList(host, frm)
        if to is not None:
            self.send_to = CommunicatorRedisList(host, to)

    def send(self, cmd):
        self.send_to.write([self.frm, cmd])

    def receive(self):
        received = self.receive_from.read()
        return received
