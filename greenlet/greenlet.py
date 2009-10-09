################
## Jae Kwon 2007
## open domain, offered as is

import thread, threading, sys
from weakref import WeakValueDictionary

class GREENLETEXCEPTION(Exception):
	pass

class GREENLETSTOP(Exception):
	pass


_thread_2_greenlet = WeakValueDictionary()
_thread_2_root_thread = {}

def getcurrent():
	current_thread = threading.currentThread()
	return _thread_2_greenlet.get(current_thread, None)

class greenlet(object):

	getcurrent = staticmethod(getcurrent)

	def _debug(self, msg):
		#print "%s visiting %s:\t%s" %(getcurrent() and getcurrent()._greenlet_name or "None", self._greenlet_name, msg)
		pass

	def __init__(self, func, name=None, implicit=False):
		"""
		func = function this greenlet should run
		implicit = is this greenlet an implicit greenlet? (for the main thread)
		"""
		#self._creator_thread = current_thread = threading.currentThread() <-- doesn't seem useful
		self._lock = threading.Semaphore(0)								# a semaphore provides us with the ability to halt threads
		self._func = func
		self._started = implicit
		self._greenlet_name = name
		self.dead = False

		self._returned_value = None
		self._raised_exception = None

		self._debug("created greenlet from %s" % str(threading.currentThread()))
		
	def bind_current_thread_to_greenlet(self, target_greenlet):
		"""
		binds the calling thread to target_greenlet, thereby capturing the thread's stack
		and getting control of it
		also bind self to thread, so it's a two way association
		"""
		captured_thread = threading.currentThread()
		if _thread_2_greenlet.get(captured_thread):
			raise GREENLETEXCEPTION, "current thread is already bound to another greenlet; this shouldn't happen"
		_thread_2_greenlet[captured_thread] = target_greenlet
		target_greenlet._bound_thread = captured_thread

	def create_new_thread_and_run(self, func, vargs, root_thread):
		"""
		create a new thread that will start running the given func with the given arguments vargs
		"""
		def wrapper():
			self.bind_current_thread_to_greenlet(self)

			assert self._first_caller_thread, "no thread initially called switch onto this greenlet? then who released this thread?"
			first_caller_greenlet = _thread_2_greenlet[self._first_caller_thread]

			# by this time we should have the arguments to func
			try:
				first_caller_greenlet._returned_value = func(*self._vargs)
			except:
				self._debug("raised.")
				first_caller_greenlet._raised_exception = sys.exc_info()
			
			# kill this greenlet; it's done running
			self.dead = True

			# now we resurrect the thread that *first* switched to this greenlet
			self._debug( "releasing thread %s" % (str(self._first_caller_thread)))
			first_caller_greenlet._lock.release()

		thread.start_new_thread(wrapper, ())

	def switch(self, *vargs, **kwargs):
		"""
		switch to this greenlet's thread, provide the arguments to give the greenlet
		"""
		# set the arguments to pass to this greenlet's func
		self._vargs = vargs
		current_thread = threading.currentThread()
		exception = kwargs.get('exception', None)
		
		if not self._started:
			self._started = True
			self._debug( "starting for first time.")

			# if this is the first time running this greenlet, it's possible that this thread is the root thread
			if not _thread_2_greenlet.get(current_thread):
				## this helps make the code concise by handling the base case in the same way as any other.
				self.parent = implicit_greenlet = greenlet(None, "^^_^^", implicit = True)
				self.bind_current_thread_to_greenlet(implicit_greenlet)
			else:
				self.parent = _thread_2_greenlet.get(current_thread)
	
			# set _first_caller_thread so we can resume this thread once self._func is done running <-- tricky!
			self._first_caller_thread = current_thread
			
			# start executing self._func in a seperate thread
			self.create_new_thread_and_run(self._func, vargs, _thread_2_root_thread.get(current_thread, current_thread)) # cool! 
		else:
			# if the root thread for this thread is not this greenlet's bound thread's root thread, crap out as per 2.6 of greenlet spec
			if _thread_2_root_thread.get(self._bound_thread, None) != _thread_2_root_thread.get(current_thread, None):	# first can't be null
				raise GREENLETEXCEPTION, "cannot mix greenlets from different threads"
		
			# set exception or return value on the 
			if exception:
				self._raised_exception = exception
			else:
				if len(vargs) == 0:
					self._returned_value = None
				elif len(vargs) == 1:
					self._returned_value = vargs[0]
				else:
					self._returned_value = vargs
				self._debug( "setting return value.")
			# switch to this greenlet by restarting its thread
			self._lock.release()

		current_thread_greenlet = _thread_2_greenlet.get(current_thread)
		# lock this thread, since we have started another <-- this was tricky
		current_thread_greenlet._lock.acquire()
		self._debug("i got freed!")

		# if we're here, then we have stuff to return 
		if current_thread_greenlet._raised_exception:
			raise current_thread_greenlet._raised_exception[0], current_thread_greenlet._raised_exception[1], current_thread_greenlet._raised_exception[2]
		else:
			return current_thread_greenlet._returned_value	

	def __del__(self):
		"""
			if this greenlet isn't dead and it gets GCed, then resume the paused thread and 
			throw a GREENLETSTOP 
		"""
		if not self.dead:
			self._raised_exception = GREENLETSTOP()
			self._lock.release()
