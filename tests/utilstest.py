import unittest
from utils.multialarm import MultiAlarm

if False:
	import logging
	logging.basicConfig()
	log = logging.getLogger()
	log.level = logging.INFO

class MultiAlarmTest(unittest.TestCase):
	
	def test_registration(self):
		alarmed = []
		alarm = MultiAlarm()
		for i in range(3):
			id = '<%s>'%i
			alarm.register(id, 1, lambda x: alarmed.append(x), id)
		import time
		time.sleep(1.5)
		
		assert set(alarmed) == set(['<0>', '<1>', '<2>'])

	def test_deregistration(self):
		alarmed = []
		alarm = MultiAlarm()
		for i in range(3):
			id = '<%s>'%i
			alarm.register(id, 1, lambda x: alarmed.append(x), id)
		import time
		time.sleep(0.5)
		for i in range(2):
			id = '<%s>'%i
			alarm.deregister(id)
		time.sleep(1.0)

		assert set(alarmed) == set(['<2>'])

if __name__ == '__main__':
	unittest.main()
