from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
# =====ENCRYPTION=====
# convert to base AES before b64 encryption
import base64
pswd="jckdvcdvbjkjkvjdjbvjkdvgbkbfjdbv"
password_in_bytes=pswd.encode("ascii")
base64Encoded=base64.b64encode(password_in_bytes)
decryptedPass=base64.b64decode(base64Encoded)
data=base64Encoded
# AES encryption
key =get_random_bytes(16)
cipher=AES.new(key,AES.MODE_EAX)
ciphertext,tag=cipher.encrypt_and_digest(data)
nonce=cipher.nonce
# this, advanceEncryption, is what we are going to store as password
advanceEncryption=ciphertext
secureStorage={
    'nonce':nonce,
    'tag':tag,
    'ciphertext':ciphertext,
    'key':key
}
# decrypting AES
cipher=AES.new(key,AES.MODE_EAX,nonce)
decryptedData=cipher.decrypt_and_verify(secureStorage['ciphertext'],secureStorage['tag'])
# ======END OF ENCRYPTION====