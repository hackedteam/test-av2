class ignore(object):
    def __init__(self, f):
        print "DBG inside myDecorator.__init__()"
        self.f = f

    def __call__(self):
        print "DBG inside myDecorator.__call__()"
        #self.f()

class testingDecorators():

	@ignore
	def myFunction():
		print "hello world"

if __name__ == '__main__':
	t = testingDecorators()
	print "CALL"
	t.myFunction()
	print "END"