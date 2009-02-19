from __future__ import with_statement
__all__ = ['states', 'multialarm', 'connections']

def preserve_signature(decorator):
	"""This decorator can be used to turn simple functions
	into well-behaved decorators, so long as the decorators
	are fairly simple. If a decorator expects a function and
	returns a function (no descriptors), and if it doesn't
	modify function attributes or docstring, then it is
	eligible to use this. Simply apply @simple_decorator to
	your decorator and it will automatically preserve the
	docstring and function attributes of functions to which
	it is applied."""
	def new_decorator(f):
		g = decorator(f)
		g.__name__ = f.__name__
		g.__doc__ = f.__doc__
		g.__dict__.update(f.__dict__)
		return g
	# Now a few lines needed to make simple_decorator itself
	# be a well-behaved decorator.
	new_decorator.__name__ = decorator.__name__
	new_decorator.__doc__ = decorator.__doc__
	new_decorator.__dict__.update(decorator.__dict__)
	return new_decorator

def randid(length=12):
	"""
		Chooses a random id of length 'length'.
		There are 62^'length' possible randids. 
		For length '12', that's 10K+ years of making a guess
		10 times a second to find a single random page, with
		a billion pages. 
	"""
	import random
	return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for x in range(length))

def threadsafe(thread_safe, threads=None):
    """
        just annotation.

        if thread_safe, then:
            if threads, only threads with these names may call this function
            if not threads, all threads may call this function
        if not thread_safe:
            if threads, threads should contain a single name, and the thread with that name owns it
            if not threads, the first thread to call this function owns it
    """
    @preserve_signature
    def wrapper(func, *vargs, **kwargs):
        return func
    return wrapper

# taken from http://www.python.org/dev/peps/pep-0343/
# we'll replace with the native version once it comes out
class GeneratorContextManager(object):
	def __init__(self, gen):
		self.gen = gen
 
	def __enter__(self):
		try:
			return self.gen.next()
		except StopIteration:
			raise RuntimeError("generator didn't yield")
 
	def __exit__(self, type, value, traceback):
		if type is None:
			try:
				self.gen.next()
			except StopIteration:
				return
			else:
				raise RuntimeError("generator didn't stop")
		else:
			try:
				self.gen.throw(type, value, traceback)
				raise RuntimeError("generator didn't stop after throw()")
			except StopIteration:
				return True
			except:
				# only re-raise if it's *not* the exception that was
				# passed to throw(), because __exit__() must not raise
				# an exception unless __exit__() itself failed.  But
				# throw() has to raise the exception to signal
				# propagation, so this fixes the impedance mismatch 
				# between the throw() protocol and the __exit__()
				# protocol.
				#
				if sys.exc_info()[1] is not value:
					raise
 
@preserve_signature
def contextmanager(func):
	def helper(*args, **kwds):
		return GeneratorContextManager(func(*args, **kwds))
	return helper

