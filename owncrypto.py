import os
import hashlib

SALT_LENGTH = 64

def saltedhash(passwd, salt):
    assert isinstance(passwd, str)
    hasher = hashlib.sha512()
    hasher.update(passwd.encode('utf-8') + salt)
    return hasher.hexdigest()

def storepassword(passw):
    salt = os.urandom(512)
    return saltedhash(passw, salt), salt

def authenticate(inputstring, storedtuple):
    return saltedhash(inputstring, storedtuple[1]) == storedtuple[0]
