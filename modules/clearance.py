import os
import time
import functools as f
import modules.owncrypto as oc
from flask import redirect, session, render_template, url_for, abort

mastersession = {} # {id: {key: value}} 
#TODO: json the userdb
userdb = {'john': {'password': oc.storepassword('pass'), 'clearances': ['theta', 'omega']}}

def assignid():
    """ Mind the side effects! """
    sessionid = os.urandom(512)
    mastersession[sessionid] = {
            'username': '',
            'authenticated': False,
            'timestamp': time.monotonic(),
        }
    session['id'] = sessionid
    return sessionid

def user():
    return mastersession[session['id']]

def require_clearance(clearance):
    def req(pageview):
        @f.wraps(pageview)
        def wrapper(*args, **kwargs):
            try:
                if user()['authenticated']:
                    if clearance in userdb[user()['username']]['clearances']:
                        return pageview(*args, **kwargs)
                    else:
                        return render_template('message.html',
                                title='Access Denied', 
                                message="You don't have the proper clearance\
                                to perform this action."), 403
            except KeyError:
                pass
            return render_template('login.html', referrer=url_for(pageview.__name__)), 401
        return wrapper
    return req

def check_clearance(clearance, referrer):
    try:
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
