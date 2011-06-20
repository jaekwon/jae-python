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
		from Crypto.Cipher import DES3
		self.cipher = DES3.new(secret, DES3.MODE_ECB)
	
	def enc(self, plaintext):
		length = len(plaintext)
		if length%8 != 0:
			padlength = 8 - length%8
			plaintext = plaintext + '\0'*padlength
		cipher = self.cipher.encrypt(plaintext)
		return base64.b64encode(cipher)[:-1].replace("+", "*").replace("/", "_")

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
		ciphertext = base64.b64decode(ciphertext.replace("*", "+").replace("_", "/")+"=")
		plaintext = self.cipher.decrypt(ciphertext).rstrip('\0')
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

if __name__ == '__main__':
  c = Crypto("q"*16)
  for i in range(10):
    print i, c.encid(i), i == c.decid(c.encid(i))
