import bcrypt
def password_hash(password):
    bytes=password.encode('utf-8')
    salt=bcrypt.gensalt()
    hash=bcrypt.hashpw(bytes,salt)
    print("bytes", bytes)
    print("salt",salt)
    print("Hash",hash.decode())
    return hash
 

 

# verify password
def password_verify(input_password,hash):
    user_bytes=input_password.encode()
    result=bcrypt.checkpw(user_bytes,hash.encode())
    print("status",result)
    return result
