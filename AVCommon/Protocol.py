class AVProtocol:
    commands = []

    def __init__(self, mq, client, commands):
        self.mq = mq
        self.client = client
        self.commands = commands

    """server side"""
    def sendCommand(self, cmd):
        self.mq.sendClient(self.client, cmd)

    """ client side """
    def receiveCommand(self):
        msg = self.mq.receiveServer()
        return msg

    """ client side """
    def answerCommand(self, reply):
        self.mq.sendServer(self.client, reply)

    """ server side """
    def receiveAnswer(self, client):
        msg = self.mq.receiveClient(self, client)
        return msg