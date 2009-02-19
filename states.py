from __future__ import with_statement

class StateException(Exception):
	pass

class IllegalStateException(StateException):
	def __init__(self, machine, bad_state):
		self.machine = machine
		self.bad_state = bad_state
		message = "cannot switch to state %s for %s" % (repr(bad_state), repr(machine))
		super(IllegalStateException, self).__init__(message)

class IllegalTransitionException(StateException):
	def __init__(self, machine, current_state, legal_states, bad_state):
		self.machine = machine
		self.current_state = current_state
		self.legal_states = legal_states
		self.bad_state = bad_state
		message = "cannot switch to state %s from %s for %s (legal: %s)" % \
			(repr(bad_state), repr(current_state), repr(machine), repr(bad_state))
		super(IllegalTransitionException, self).__init__(message)

class UndefinedTransitionException(StateException):
	def __init__(self, machine, current_state, transition_rule):
		self.machine = machine
		self.current_state = current_state
		self.transition_rule = transition_rule
		message = "transition rule is undefined for state %s on %s (transition_rule: %s)" % \
			(repr(current_state), repr(machine), repr(transition_rule))
		super(UndefinedTransitionException, self).__init__(message)

class StateMachine(object):
	"""
		manages various state machine related mechanisms.
		usages:
		 - define a set of possible states, and switch between them
		 - threadsafe
	"""
	def __init__(self, states=None, start=None, rules=None):
		"""
			states: 
			 - if not None, a set of all legal states.
			 - if None, there are no limitations

			start: the initial state

			rules: a dict of state transition rules
			 {
			  <state1>: set(<next_state1>, <next_state2>, ...),
			  <state2>: None, # GOES NOWHERE
			 }
			 - if 'rules' is present but 'states' is not, 'states' is generated.
			 - if 'rules' and 'states' are both specified, must be consistent.
			 - if 'rules' is missing any value for a legal state, then the machine can transition
			   to any legal state.
		"""
		if rules is not None and states is None:
			states = self._derive_states_from_rules(rules)
		if states is not None:
			if start not in states:
				raise IllegalStateException(self, start)
		self.states = states is not None and frozenset(states) or None
		self.current = start
		self.rules = rules is not None and dict(rules) or None
		import threading
		self.__lock = threading.RLock()

	@property
	def next_states(self):
		"""
			if self.rules, consults that. 
			if all states are game, returns an immutable copy of self.states
			otherwise returns None
		"""
		current_state = self.current
		if self.rules is not None:
			if self.rules.has_key(current_state):
				return frozenset(self.rules[current_state]) or frozenset()
			else:
				return self.states
		else:
			return self.states

	def _derive_states_from_rules(self, rules):
		# check all states mentioned in the rules dict
		states = set()
		for key, states in rules.iteritems():
			states.add(key)
			if states:
				for state in states:
					states.add(state)
		return states

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
			self._check(new_state)
			self.current = new_state

	def switch_by(self, transition_rule):
		"""
			transition_rule: a dict of 
			 {
			   <from_state>: <to_state>,
			   ...
			 }
			 - transition_rule does not have to contain rules for all states; it
			   just needs to contain at least the rule for self.current
		
			raises UndefinedTransitionException
		"""
		with self.__lock:
			if not transition_rule.has_key(self.current):
				raise UndefinedTransitionException(self, self.current, transition_rule)
			else:
				next_state = transition_rule[self.current]
				self.switch(next_state)

del with_statement
