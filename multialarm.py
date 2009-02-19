from __future__ import with_statement
import heapq
import time
from utils import randid

class MultiAlarm(object):
	"""
		An optimized Timer-like object that manages multiple alarm actions on a single thread.
		Desirable when alarm-ringing events are expected to be rare.

		All alarm callables will be called on from a private thread.
		You can overwrite alarms by setting new callable/vargs/kwargs/timeouts.
	"""	
	import logging
	log = logging.getLogger()

	def __init__(self, sleep_step=0.1):
		## expiration_*
		self.expiration_heap = []       # stores items (expiration, id, tix, callable, vargs, kwargs)
		self.expiration_tix_lookup = {} # stores id:tix
		self.sleep_step = sleep_step
		import thread, threading
		self.__cond_alarm_sleep = threading.Condition()
			# we'd use an Event object, but we need to do some interlapping locking
		self.__lock_expiration = threading.RLock()
		self.__alarm_thread_stop = False
		self.__alarm_thread = thread.start_new_thread(self._check_alarms, ())

	def __del__(self):
		if hasattr(self, '__alarm_thread_stop'):
			self.__alarm_thread_stop = True
		if hasattr(self, '__cond_alarm_sleep'):
			with self.__cond_alarm_sleep:
				self.__cond_alarm_sleep.wait()
		super(MultiAlarm, self).__del__()
	
	def _check_alarms(self):
		while not self.__alarm_thread_stop:
			try:
				# states to fill with lock_expiration
				alarm_item = None           # if we are going to ring an alarm, this will be populated.
				alarm_should_sleep = False  # if true, this alarm will sleep

				with self.__lock_expiration:
					if self.expiration_heap:
						expiration, id, tix, _, _, _ = self.expiration_heap[0]
						current_tix = self.expiration_tix_lookup.get(id)
						now = time.time()
						if now > expiration:
							# this is the only case when the alarm will ring
							if current_tix == tix:
								self.log.info('now > expiration, tix matched, time to ring it')
								del self.expiration_tix_lookup[id]
								alarm_item = heapq.heappop(self.expiration_heap)
							else:
								self.log.info('expiration %s now %s current_tix %s tix %s' % (expiration, now, current_tix, tix) )
								self.log.info('expiration or tix does not match')
								# we just pop the item, we don't need it
								_ = heapq.heappop(self.expiration_heap)
					else:
						self.log.info('we should to go sleep')
						# nothing happens, alarm_item doesn't get set, and we sleep
						# but, we need to acquire the alarm_sleep lock to make sure registrations don't happen
						self.__cond_alarm_sleep.acquire()
						alarm_should_sleep = True

				if alarm_should_sleep:
					# cond_alarm_sleep was acquired with lock_expiration
					self.__cond_alarm_sleep.wait()
					self.__cond_alarm_sleep.release()									
				elif alarm_item:
					# now, outside lock_expiration, call the callable
					# TODO consider a pool of threads?
					_, _, _, callable, vargs, kwargs = alarm_item
					callable(*vargs, **kwargs)
				else:
					# we should sleep for a small timestep
					# TODO consider an intelligent sleep time progression
					time.sleep(self.sleep_step)
			except Exception, e:
				self.log.error(e)

	def register(self, id, timeout, callable, *vargs, **kwargs):
		with self.__lock_expiration:
			# should the alarm thread be sleeping, we wake it up.
			with self.__cond_alarm_sleep:
				self.__cond_alarm_sleep.notifyAll()
			# push the new alarm_item to the heap
			now = time.time()
			tix = "tix" + randid()
			heapq.heappush(self.expiration_heap, (now + timeout, id, tix, callable, vargs, kwargs) )
			self.expiration_tix_lookup[id] = tix

	def deregister(self, id):
		with self.__lock_expiration:
			if self.expiration_tix_lookup.has_key(id):
				del self.expiration_tix_lookup[id]

alarm = MultiAlarm()

del with_statement
