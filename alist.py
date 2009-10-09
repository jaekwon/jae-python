# an ordered dict with some intelligence

class AssociativeList(object):
	""" basically an ordered dict you can use as an array.
		alist.append( key, value )
		alist.extend( [(key, value), (key, value), ...] )
		alist[key] = value <- appends as well
		alist[key] = value <- duplicate entry will remove the old item
		alist.append( {'id': _, 'blah': _} ) <- will assume key is value of 'id', and the entire dict the value
		alist.extend( [{'id': ...}, ...] ) <- same
	"""
	def __init__(self, some_list=None):
		self.list = []
		self.lookup = {}
		if some_list:
			self.extend(some_list)

	def _to_tuple(self, item):
		if len(item) == 1:
			key = item[0]['id']
			value = item[0]
		elif len(item) == 2:
			key = item[0]
			value = item[1]
		else:
			raise AssertionError, "append expects 1 or 2 item"
		return (key, value)

	def _add_item(self, key, value):
		self.lookup.setdefault(key, []).append(value)
		self.list.append( (key, value) )

	def __len__(self):
		return len(self.list)

	def __iter__(self):
		return iter(self.list)

	def item_at(self, index):
		return self.list[index]

	def append(self, *vargs):
		self._add_item( *self._to_tuple(vargs) )
	
	def extend(self, a_list):
		for item in a_list:
			self._add_item( *self._to_tuple(item) )

	def __setitem__(self, key, value):
		self.append( key, value )

	def __getitem__(self, key):
		return self.lookup[key]

	def __contains__(self, value):
		""" ambiguous. be cautious """
		if isinstance(value, tuple):
			# first pretend that value is a key-value tuple
			if value in self.list:
				return True
		return value in self.lookup

	def get(self, key, default=None):
		return self.lookup.get(key, default)

	def set(self, key, value):
		self.append( key, value )

	# XXX implement remove, del, etc

	def __str__(self):
		return '\n'.join(str(x) for x in self.list)
