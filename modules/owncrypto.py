import bcrypt
from modules.config import conf

def storepassword(inputstring):
    passw = inputstring.encode('utf-8')
    return bcrypt.hashpw(passw, bcrypt.gensalt(conf['bcryptfactor']))

def authenticate(inputstring, stored):
    passw = inputstring.encode('utf-8')
    return bcrypt.hashpw(passw, stored) == stored
