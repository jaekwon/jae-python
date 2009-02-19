from __future__ import with_statement
import unittest
from utils.connections import ConnectionPool

class TestPool(ConnectionPool):
	
	def __init__(self, max_connections):
		super(TestPool, self).__init__(max_connections)
		self.num_connections = 0
	
	def make_connection(self):

		# you can't set attributes directly on object instances, so we need a dummy subclass
		class TestConnection(object):
			pass

		self.num_connections += 1
		return TestConnection()
		

class ConnectionPoolTest(unittest.TestCase):

	def setUp(self):
		self.testpool = TestPool(10)

	def testLimitOneThread(self):
		# we have a thread repeatedly make connections.
		# after 10, the thread should hang (since we're not returning them)
		# and there should have been 10 connections made in self.testpool.
		
		def make_connections():
			while True:
				newconn = self.testpool.get_connection()
		
		import thread
		thread.start_new_thread(make_connections, ())

		# may connections be made
		import time
		time.sleep(3)
	
		# may there only be 10 connections made
		assert self.testpool.num_connections == 10, "expected 10 connections to be made"

	def testLimitTwoThreads(self):
		# same as above but with two simutaneous connections
		
		def make_connections():
			while True:
				newconn = self.testpool.get_connection()
				import time
				time.sleep(0.1)
		
		import thread
		thread.start_new_thread(make_connections, ())
		thread.start_new_thread(make_connections, ())

		# may connections be made
		import time
		time.sleep(3)
			# must sleep for longer than 0.1 * 10 = 1 second
	
		# may there only be 10 connections made
		assert self.testpool.num_connections == 10, "expected 10 connections to be made"

	def testReturnOneThread(self):
		# try returning some connections, make sure the limit doesn't get reached.

		all_connections = set()
		
		def make_or_return_connections():
			import threading
			lock__make_return = threading.RLock()			

			while True:
				with lock__make_return:
					import random
					if random.random() > 0.5:
						try:
							# return a connection if it exists
							connection = all_connections.pop()
							self.testpool.return_connection(connection)
						except KeyError:
							pass # oh well
					else:
						connection = self.testpool.get_connection()
						all_connections.add(connection)
					# print len(all_connections)
						# if you uncomment the above line,
						# you should see the number of connections go up and down and 
						# most likely reach 10 and halt.

		# start some threads that sometimes makes and sometimes returns connections
		import thread
		thread.start_new_thread(make_or_return_connections, ())
		thread.start_new_thread(make_or_return_connections, ())
		thread.start_new_thread(make_or_return_connections, ())

		# wait a while
		import time
		time.sleep(5)
		
		# we should not have created more than 10 connections
		assert self.testpool.num_connections <= 10, "expected less than 10 connections created overall"

if __name__ == '__main__':
    unittest.main()
