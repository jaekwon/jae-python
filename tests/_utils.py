#from __future__ import with_statement

def throwing(exception_class):
	"""
		to be used as a 'with' context

		usage: 
		 with throwing(ValueError):
		     # something that should throw a ValueError
	"""
	class context(object):
		def __enter__(self):
			pass
		def __exit__(self, *vargs, **kwargs):
			exc_class, exc, traceback = vargs
			if exception_class is None and exc is not None:
				raise AssertionError, "expected no exception but was thrown [%s]" % exc
			elif isinstance(exc, exception_class):
				return True # swallow exception
			else:
				raise AssertionError, "expected exception was not thrown"
	return context()
