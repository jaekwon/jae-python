from __future__ import with_statement
import unittest

from _utils import throwing
from utils.crypto import Crypto, CryptoException

class CryptoTest(unittest.TestCase):

	def testEncDec(self):
		c = Crypto('some secret key_')
		plaintext = 'foo'
		ciphertext = c.enc(plaintext)
		plaintext2 = c.dec(ciphertext)
		assert plaintext == plaintext2

	def testEncidDecid(self):
		c = Crypto('some secret key_')
		plaintext = 1
		ciphertext = c.encid(plaintext)
		plaintext2 = c.decid(ciphertext)
		assert plaintext == plaintext2

	def testEncidBad(self):
		# try encoding a non integer
		c = Crypto('some secret key_')
		plaintext = 'foo'
		with throwing(CryptoException):
			ciphertext = c.encid(plaintext)

	def testDecidBad(self):
		# try decoding a non integer ciphertext
		c = Crypto('some secret key_')
		plaintext = 'foo'
		ciphertext = c.enc(plaintext)
		with throwing(CryptoException):
			plaintext2 = c.decid(ciphertext)

if __name__ == '__main__':
	unittest.main()

