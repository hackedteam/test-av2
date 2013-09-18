import Command


class Command_END(Command.Command):

    """ server side """
    def onInit(self):
        print "    CS onInit"
        pass

    def onAnswer(self, answer):
        print "    CS onAnswer"

    """ client side """
    def Execute(self):
        print "    CS Execute"

        return True, ""


