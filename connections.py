from __future__ import with_statement

class ConnectionPool(object):
	"""
		an abstract class that is meant to be extended.
		override the 'make_connection' method.

		threads should use connections and then return them after use.
		if a connection is not properly returned, they automatically get recycled
		after a timeout.

		sets attributes like 'cp_checkout_time' on the connection object.
		(connection object must be a subclass of 'object')

		TODO: timeout stuff is not implemented.
	"""
	
	def __init__(self, max_connections, timeout=None):
		import threading
		self.max_connections = max_connections
		self.timeout = timeout

		self.connections = set()
		self.available_connections = set()
		self.connection_semaphore = threading.Semaphore(max_connections)
		self.lock__checkin_checkout = threading.RLock()
			# mainly because of setting / unsetting the checkout time.

	def make_connection(self):
		raise NotImplemented, "forgot to subclass?"

	def get_connection(self):
		with self.lock__checkin_checkout:
			self.connection_semaphore.acquire()
			try:
				connection = self.available_connections.pop()
			except KeyError:
				connection = self.make_connection()
				self.connections.add(connection)
				import logging
				logging.info("making a new connection for connection pool")
			import time
			connection.cp_checkout_time = time.time()
			return connection

	def return_connection(self, connection):
		with self.lock__checkin_checkout:
			connection.cp_checkout_time = None
			self.available_connections.add(connection)
			self.connection_semaphore.release()

del with_statement
