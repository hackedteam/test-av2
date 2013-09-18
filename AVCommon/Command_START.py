import Command


class Command_START(Command.Command):

    """ server side """
    def onInit(self):
        print "    CS onInit"
        pass

    def onAnswer(self, answer):
        print "    CS onAnswer"

    """ client side """
    def Execute(self):
        print "    CS Execute"
        return True, "I'm doing Science and I'm alive"


