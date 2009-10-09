from __future__ import with_statement
import unittest
from utils import states

class StatesTest(unittest.TestCase):

	def testNoLimit(self):
		smachine = states.StateMachine()
		assert smachine.current is None

		def switch_and_assert(new_state):
			smachine.switch(new_state)
			assert smachine.current == new_state
			assert smachine.next_states == None
	
		for new_state in ['foo', 'bar', 'baz', None, 'baz']:
			switch_and_assert(new_state)	

	def testBadStartState(self):
		all_states = ['foo', 'bar', 'baz']

		with throwing(states.IllegalStateException):
			# should throw because 'None' is not in the default state
			smachine = states.StateMachine(all_states)

		smachine = states.StateMachine(all_states, 'foo')
		assert smachine.current == 'foo'

	def testIllegalTransitionException(self):
		# testing attempts to switch to states not allowed by the 
		# restrictions dict.
		restrictions = {'foo': 'bar',          # foo must go to bar
						'bar': ['foo', 'baz'], # bar must go to foo or baz
						'baz': None}           # baz is the end state
		smachine = states.StateMachine(start='foo', restrictions=restrictions)
		smachine.switch('bar')
		smachine.switch('foo')
		with throwing(states.IllegalTransitionException):
			smachine.switch('baz')
		smachine.switch('bar')
		smachine.switch('baz')
		with throwing(states.IllegalTransitionException):
			smachine.switch('foo')
		with throwing(states.IllegalTransitionException):
			smachine.switch('bar')
		smachine.switch('baz') # does nothing
		smachine.switch('baz') # does nothing

	def testTransitionRules(self):
		# testing the 'switch_by' method
		smachine = states.StateMachine(start=1)
		rules_1 = {1:2, 2:3, 3:1}
		rules_2 = {1:3, 3:2, 2:1}

		for i in [2, 3, 1]:
			smachine.switch_by(rules_1)
			assert smachine.current == i
		
		for i in [3, 2, 1]:
			smachine.switch_by(rules_2)
			assert smachine.current == i

	def testBadTransitionRules(self):
		# bad because current is not in keys
		smachine = states.StateMachine(start='foo')
		
		with throwing(states.UndefinedTransitionException):
			smachine.switch_by({'_': '_'})

def throwing(exception_class):
	"""
		to be used as a 'with' context. see python's 'with_statement'
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

if __name__ == '__main__':
	unittest.main()

