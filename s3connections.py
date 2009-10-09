from __future__ import with_statement
from utils.connections import ConnectionPool
from boto.s3 import Connection, Key

class S3ConnectionPool(ConnectionPool):
	"""
		returns boto s3 connections
	"""

	def __init__(self, aws_credentials, max_connections, timeout=None):
		super(S3ConnectionPool, self).__init__(max_connections, timeout)
		self.aws_credentials = aws_credentials

	def a_connection(self):
		"""
			for use with with_statement, so it looks like:
			
			with S3CP.a_connection():
				pass
		"""
		s3cp = self # i'd rather do this than change 'self' below
		class ConnectionContext(object):
			def __init__(self):
				self.conn = None
			def __enter__(self):
				self.conn = s3cp.get_connection()
				return self.conn
			def __exit__(self, *vargs):
				s3cp.return_connection(self.conn)
				self.conn = None
		return ConnectionContext()

	def a_bucket(self, bucket_name):
		"""
			for use with with_statement, see 'a_connection' for details.
		"""
		s3cp = self
		class ConnectionContext(object):
			def __init__(self):
				self.conn = None
				self.bucket = None
			def __enter__(self):
				self.conn = s3cp.get_connection()
				self.bucket = self.conn.get_bucket(bucket_name, False)
				return self.bucket
			def __exit__(self, *vargs):
				s3cp.return_connection(self.conn)
				self.conn = None
				self.bucket = None
		return ConnectionContext()

	def a_key(self, bucket_name, key):
		s3cp = self
		class ConnectionContext(object):
			def __init__(self):
				self.conn = None
				self.bucket = None
			def __enter__(self):
				self.conn = s3cp.get_connection()
				self.bucket = self.conn.get_bucket(bucket_name, False)
				self.key = Key(self.bucket, key)
				return self.key
			def __exit__(self, *vargs):
				try:
					self.key.close()
				except:
					import logging
					import traceback
					logging.warn('some kind of error closing a key:\n%s', traceback.format_exc())
				s3cp.return_connection(self.conn)
				self.conn = None
				self.bucket = None
				self.key = None
		return ConnectionContext()

	def make_connection(self):
		return Connection(self.aws_credentials[0], self.aws_credentials[1], False)	

del with_statement
