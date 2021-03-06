import os
import time
import functools as f
import modules.owncrypto as oc
from modules.config import conf
from flask import redirect, session, render_template, url_for, abort

mastersession = {} # {id: {key: value}}
#TODO: json the userdb
userdb = {'john': {'password': oc.storepassword('pass'), 'clearances': ['theta', 'omega']}}
dummy = oc.storepassword('correcthorsebatterystaple')

def assignid():
    """ Mind the side effects! """
    sessionid = os.urandom(512)
    mastersession[sessionid] = {
            'username': '',
            'authenticated': False,
            'timestamp': time.time(),
            'ip': '',
            'fails': 0,
        }
    session['id'] = sessionid
    return sessionid

def user():
    return mastersession[session['id']]

def check_clearance(clearance, referrer):
    try:
        if time.time() - user()['timestamp'] > conf['maxsessionage']:
            return render_template('login.html', referrer=referrer), 401
        if user()['authenticated']:
            if clearance in userdb[user()['username']]['clearances']:
                return False
            else:
                return render_template('message.html',
                        title='Access Denied',
                        message="You don't have the proper clearance\
                        to perform this action."), 403
    except KeyError:
        pass
    return render_template('login.html', referrer=referrer), 401

def require_clearance(clearance):
    def req(pageview):
        @f.wraps(pageview)
        def wrapper(*args, **kwargs):
            referrer = url_for(pageview.__name__)
            check = check_clearance(clearance, referrer)
            if check:
                return check
            else:
                return pageview(*args, **kwargs)
        return wrapper
    return req

def bucket_clearance(clearances):
    def checker(pageview):
        @f.wraps(pageview)
        def wrapper(*args, **kwargs):
            bucketname = kwargs['bucketname']
            try:
                entname = kwargs['entkey']
            except KeyError:
                entname = ''
            try:
                clearance = clearances[bucketname]
            except KeyError:
                return abort(404)
            if clearance:
                check = check_clearance(clearance, 
                        '/b/%s' % bucketname + '/%s' % entname * bool(entname))
                if check:
                    return check
            return pageview(*args, **kwargs)
        return wrapper
    return checker
