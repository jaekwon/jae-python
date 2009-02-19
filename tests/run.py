import unittest
import utils.tests

suite = unittest.defaultTestLoader.loadTestsFromModule(utils.tests)
unittest.TextTestRunner(verbosity=2).run(suite)
