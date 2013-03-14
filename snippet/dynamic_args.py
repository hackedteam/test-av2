def foo(k, *params):
	print params


foo(k="one")
foo("one","two")
foo("one","two","three")
foo("one","two","three","four")