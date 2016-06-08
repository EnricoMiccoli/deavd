import os
import time
from deavd import * # necessary to properly unpickle
import owncrypto as oc
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask.ext.scss import Scss


app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(512)

Scss(app, asset_dir='./')

BUCKETDIR = 'buckets/'

# {id: {key: value}} 
mastersession = {}
passdb = {'user': oc.storepassword('pass')}

def assignid():
    """ Mind the side effects! """
    sessionid = os.urandom(512)
    mastersession[sessionid] = {
            'username': '',
            'authenticated': 0,
            'timestamp': time.monotonic(),
        }
    session['sessionid'] = sessionid
    return sessionid

@app.route('/test')
def testpage():
    try:
        return 'You are ' +  mastersession[session['sessionid']]['username'] + ' and you are ' + 'not ' * int(not mastersession[session['sessionid']]['authenticated']) + 'authenticated'
    except KeyError:
        return "Who the hell are you"

@app.route('/login', methods=['POST'])
def login():
    sessionid = assignid()
    password = request.form['password']
    username = request.form['username']
    try:
        if oc.authenticate(password, passdb[username]):
            mastersession[sessionid]['username'] = username
            mastersession[sessionid]['authenticated'] = 1
            return "You have logged in"
    except KeyError:
        pass
    return "Invalid credentials"

@app.route('/login')
def loginpage():
    return render_template('login.html')

@app.route('/')
def homepage():
    return render_template('homepage.html', buckets=['shapes'])

@app.route('/b/<bucketname>')
def bucketpage(bucketname=None):
    try:
        bucket = loadbucket(BUCKETDIR + bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    return render_template('bucketpage.html', bucket=bucket)

@app.route('/b/<bucketname>', methods=['POST'])
def bucketquery(bucketname=None):
    try:
        bucket = loadbucket(BUCKETDIR + bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)

    stringquery = request.form['query']
    if not stringquery: # checks for empty query
        return render_template('bucketpage.html', bucket=bucket, prevsearch='')
    else:
        query = parsequery(stringquery)
        result = Bucket('Results of your query')
        try:
            result.update((key, bucket[key]) for key in bucket.query(query))
        except QueryError:
            return 'Invalid operator in query ' + query

        # check if empty
        if result:
            return render_template('bucketpage.html', bucket=result, prevsearch=stringquery)
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

if __name__ == '__main__':
    app.run()
