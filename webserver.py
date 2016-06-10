import os
import time
from deavd import * # necessary to properly unpickle
import functools as f
import owncrypto as oc
from flask import Flask
from flask.ext.scss import Scss
from flask import render_template, redirect, url_for, request, session

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(512)

Scss(app, asset_dir='./')

BUCKETDIR = 'buckets/'

# {id: {key: value}} 
mastersession = {}
passdb = {'user': oc.storepassword('pass')}
clearancedb = {'user': set(['theta'])}

def assignid():
    """ Mind the side effects! """
    sessionid = os.urandom(512)
    mastersession[sessionid] = {
            'username': '',
            'authenticated': 0,
            'timestamp': time.monotonic(),
        }
    session['id'] = sessionid
    return sessionid

def server_session():
    return mastersession[session['id']]

def require_clearance(level):
    def req(pageview):
        @f.wraps(pageview)
        def wrapper(*args, **kwargs):
            try:
                if server_session()['authenticated']:
                    if level in clearancedb[server_session()['username']]:
                        return pageview(*args, **kwargs)
                    else:
                        return render_template('message.html', title='Access Denied', message="You don't have the proper clearance to access this information."), 403
            except KeyError:
                pass
            return render_template('login.html', referrer=url_for(pageview.__name__)), 401
        return wrapper
    return req

@app.route('/theta')
@require_clearance('theta')
def theta():
    return 'this is theta secret'

@app.route('/delta')
@require_clearance('delta')
def delta():
    return 'this is a delta secret'

@app.route('/test')
def testpage():
    try:
        return render_template('message.html', title='Credential Check', message='You are ' +  mastersession[session['id']]['username'] + ' and you are ' + 'not ' * int(not mastersession[session['id']]['authenticated']) + 'authenticated with ' + ', '.join([x for x in clearancedb[server_session()['username']]]))
    except KeyError:
        return "Who the hell are you"

@app.route('/login', methods=['POST'])
def login(referrer=None):
    sessionid = assignid()
    password = request.form['password']
    username = request.form['username']
    try:
        if oc.authenticate(password, passdb[username]):
            mastersession[sessionid]['username'] = username
            mastersession[sessionid]['authenticated'] = 1
            return redirect(request.form['referrer'], 302)
    except KeyError:
        pass
    return render_template('message.html', title="Invalid credentials")

@app.route('/login')
def loginpage():
    return render_template('login.html')

@app.route('/logout')
def logoutpage():
    mastersession.pop(session['id'])
    return render_template('message.html', title="Logged out", message="You have succesfully logged out")

@app.route('/')
def homepage():
    return render_template('homepage.html', buckets=['shapes'])

@app.route('/b/<bucketname>')
def bucketpage(bucketname=None):
    try:
        bucket = loadbucket(BUCKETDIR + bucketname)
        fbp = bucket.path # Father bucket path
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    return render_template('bucketpage.html', bucket=bucket, fbp=fbp)

@app.route('/b/<bucketname>', methods=['POST'])
def bucketquery(bucketname=None):
    try:
        bucket = loadbucket(BUCKETDIR + bucketname)
        fbp = bucket.path # Father bucket path
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)

    stringquery = request.form['query']
    if not stringquery: # checks for empty query
        return render_template('bucketpage.html', bucket=bucket, prevsearch='', fbp=fbp)
    else:
        query = parsequery(stringquery)
        result = Bucket('Results of your query')
        try:
            result.update((key, bucket[key]) for key in bucket.query(query))
        except QueryError:
            return 'Invalid operator in query ' + query

        # check if empty
        if result:
            return render_template('bucketpage.html', bucket=result, prevsearch=stringquery, fbp=fbp)
        else: 
            return render_template('bucketpage.html', bucket=result, prevsearch=stringquery, empty=True)

@app.route('/b/<bucketname>/<entkey>')
def entpage(bucketname=None, entkey=None):
    try:
        bucket = loadbucket(BUCKETDIR + bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    try:
        entity = bucket[entkey]
    except KeyError:
        return render_template('noentityfound.html', bucketname=bucketname, entityname=entityname) 
    return render_template('entitypage.html', bucketname=bucket.name, ent=entity)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('message.html', title="Page not found", message="The resource you requested is not present on the server.", link=[url_for('homepage'), "Go back home"]), 404

if __name__ == '__main__':
    app.run()
