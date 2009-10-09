##
## handles encrypting and decrypting strings (usually integer ids)
##

import base64

class CryptoException(Exception):
	pass

## TODO this shit isn't implemented
class Crypto(object):
	"""
		usage:
		 e = Crypto(<secret str>)
		 id = 'foo'
		 encid = e.enc(id)
		 decid = e.dec(encid)
		 assert id == decid

		 id = 1
		 encid = e.encid(id)
		 decid = e.decid(encid)
		 assert id == decid # 'decid' produces an integer
	"""
	def __init__(self, secret):
		self.__secret = secret
		from Crypto.Cipher import AES
		self.aes = AES.new(secret, AES.MODE_ECB)
	
	def enc(self, plaintext):
		length = len(plaintext)
		if length%16 != 0:
			padlength = 16 - length%16
			plaintext = plaintext + '\0'*padlength
		cipher = self.aes.encrypt(plaintext)
		return base64.b32encode(cipher)[:-6]

	def encid(self, plaintext):
		if not isinstance(plaintext, (int, long)):
			raise CryptoException, "not a valid id: %s" % plaintext
		return self.enc(str(plaintext))

	def encids(self, plaintexts):
		return [self.encid(x) for x in plaintexts]

	def encid_safe(self, plaintext):
		if plaintext is None: return None
		return self.encid(plaintext)

	def dec(self, ciphertext):
		ciphertext = base64.b32decode(ciphertext+"======")
		plaintext = self.aes.decrypt(ciphertext).rstrip('\0')
		return plaintext

	def decid(self, ciphertext):
		plaintext = self.dec(ciphertext)
		try:
			return int(plaintext)
		except ValueError:
			raise CryptoException, "not a valid encrypted id: %s" % ciphertext

	def decid_safe(self, ciphertext):
		if ciphertext is None: return None
		return self.decid(ciphertext)
