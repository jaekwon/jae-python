from __future__ import with_statement

__doc__ = \
"""
Manages state and transitions in a threadsafe manner.

A StateMachine instance keeps track of its current state, the set of all
possible states, and transition restrictions. Each state is any hashable /
comparable object that is not a set or a list (ideally just a string).

Usage: define a set of possible states, and switch between them

# create a state machine
sm = StateMachine(states=['start', 'middle', 'end'], start='start')
sm.current // 'start'

# switch to some state
sm.switch('end') // OK
sm.switch('foo') // raises IllegalStateException, 'foo' is not defined.

# switch using some transition table
sm.switch('start')
transition_table = {'start': 'middle',
				   'middle': 'end'} // 'end' doesn't go anywhere
sm.switch_by(transition_table)
sm.current // 'middle'
sm.switch_by(transition_table)
sm.current // 'end'
sm.switch_by(transition_table) // raises UndefinedTransitionException

# create a state machine with no defined states
sm2 = StateMachine(start='foo')

# create a state machine with restrictions
restrictions = {'IDLE': 'SENDING_REQUEST',
				'SENDING_REQUEST': ['AWAITING_RESPONSE', 'ERROR'],
				'AWAITING_RESPONSE': ['RECEIVED_RESPONSE', 'TIMEOUT', 'ERROR'],
				'RECEIVED_RESPONSE': 'IDLE'}
sm3 = StateMachine(restrictions=restrictions, start='IDLE') // possible states are inferred from 'restrictions'
sm3.switch('SENDING_REQUEST') // OK
sm3.switch('IDLE') // raises InvalidTransitionException
sm3.switch_by({'SENDING_REQUEST': 'AWAITING_RESPONSE'}) // switch_by still works
sm3.switch_by({'AWAITING_RESPONSE': 'IDLE'}) // still raises IllegalTransitionException, due to 'restrictions'
"""

class StateException(Exception):
	""" Base Exception class for the StateMachine class """
	pass

class IllegalStateException(StateException):
	""" Exception raised when trying to switch to an illegal (unknown) state """
	def __init__(self, machine, bad_state):
		self.machine = machine
		self.bad_state = bad_state
		message = "cannot switch to state %s for %s" % (repr(bad_state), repr(machine))
		super(IllegalStateException, self).__init__(message)

class IllegalTransitionException(StateException):
	""" Exception raised when trying to make an illegal transition """
	def __init__(self, machine, current_state, legal_states, bad_state):
		self.machine = machine
		self.current_state = current_state
		self.legal_states = legal_states
		self.bad_state = bad_state
		message = "cannot switch to state %s from %s for %s (legal: %s)" % \
			(repr(bad_state), repr(current_state), repr(machine), repr(bad_state))
		super(IllegalTransitionException, self).__init__(message)

class UndefinedTransitionException(StateException):
	"""
		When calling <state_machine>.switch_by(transition_table), if the 
		current state is not present in 'transition_table', this exception is raised
	"""
	def __init__(self, machine, current_state, transition_table):
		self.machine = machine
		self.current_state = current_state
		self.transition_table = transition_table
		message = "transition rule is undefined for state %s on %s (transition_table: %s)" % \
			(repr(current_state), repr(machine), repr(transition_table))
		super(UndefinedTransitionException, self).__init__(message)

class StateMachine(object):
	"""
		The main StateMachine class
	"""
	def __init__(self, states=None, start=None, restrictions=None, ignore_duplicate_switches=True):
		"""
			states: 
			 - if not None, a set of all legal states.
			 - if None, any state is possible.

			start: the initial state. 
			 (you almost always want to specify this, unless None is a valid state!)

			restrictions: a dict of state transition restrictions
			 {
			  <state1>: set(<next_state1>, <next_state2>, ...),
			  <state2>: None, # end state, no further transitions possible
			 }
			 - if 'restrictions' and 'states' are both specified, must be consistent.
			 - if 'restrictions' is undefined for the current state, any transition is legitimate
			 - if restrictions[self.current] == None, no further transitions are possible.

			ignore_duplicate_switches: if True, switching to the current state is ALWAYS ok
			 ('restrictions' is ignored)
		"""
		restrictions = self._normalize_restrictions_dict(restrictions)
		if restrictions is not None and states is None:
			states = self._derive_states_from_restrictions(restrictions)
		if states is not None:
			if start not in states:
				raise IllegalStateException(self, start)
		self.states = states is not None and frozenset(states) or None
		self.current = start
		self.restrictions = restrictions is not None and dict(restrictions) or None
		self.ignore_duplicate_switches = ignore_duplicate_switches
		import threading
		self.__lock = threading.RLock()

		# for push/pop operations...
		self.attr = {}
		self.stack = [] # list of (state, attributes) tuples

	@property
	def next_states(self):
		"""
			Consults self.restrictions to find set of next possible states
			Otherwise returns self.states (the set of all possible states), or None
		"""
		current_state = self.current
		if self.restrictions is not None:
			if self.restrictions.has_key(current_state):
				return frozenset(self.restrictions[current_state]) or frozenset()
			else:
				return self.states
		else:
			return self.states

	def _normalize_restrictions_dict(self, restrictions):
		# given 'restrictions' which may have values of 
		# type 'list', 'set', or other,
		# returns a dict where the values are sets.
		if not restrictions: return None
		normalized = {}
		for key, value in restrictions.iteritems():
			if isinstance(value, list):
				value = set(value)
			elif isinstance(value, set):
				pass
			else:
				value = set([value])
			normalized[key] = value
		return normalized	

	def _derive_states_from_restrictions(self, restrictions):
		# check all states mentioned in the restrictions dict
		all_states = set()
		for key, states in restrictions.iteritems():
			all_states.add(key)
			if states:
				for state in states:
					all_states.add(state)
		return all_states

	def _check(self, new_state):
		# make sure new_state is legal
		if self.states is not None:
			if new_state not in self.states:
				raise IllegalStateException(self, new_state)
		# make sure transition is legal
		legal_transitions = self.next_states
		if legal_transitions is not None:
			if new_state not in legal_transitions:
				raise IllegalTransitionException(self, self.current, legal_transitions, new_state)
	
	def switch(self, new_state):
		with self.__lock:
			if self.ignore_duplicate_switches:
				if self.current == new_state:
					return
			self._check(new_state)
			self.current = new_state

	def push(self, new_state):
		with self.__lock:
			self.stack.append((self.current, self.attr))
			self.attr = {}
			self.current = new_state

	def pop(self, new_state):
		"""
			you can always pop to a previous state regardless of restrictions
		"""
		with self.__lock:
			self.current, self.attr = self.stack.pop()

	def switch_by(self, transition_table):
		"""
			transition_table: a dict of 
			 {
			   <from_state>: <to_state>,
			   ...
			 }
			 - transition_table does not have to contain rules for all states; it
			   just needs to contain at least the rule for self.current
		
			raises UndefinedTransitionException
		"""
		with self.__lock:
			if not transition_table.has_key(self.current):
				raise UndefinedTransitionException(self, self.current, transition_table)
			else:
				next_state = transition_table[self.current]
				self.switch(next_state)

	def __getitem__(self, key, default):
		return self.attr.get(key, default)

	def __setitem__(self, key, value):
		self.attr[key] = value

del with_statement
