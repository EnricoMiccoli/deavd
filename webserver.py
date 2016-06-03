import os
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

@app.route('/test')
def testpage():
    try:
        return session['username']
    except KeyError:
        return "You aren't logged in"

@app.route('/login/<user>/')
def login(user=None, var=None):
    session['username'] = user
    return "logged in"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return 'You have logged out'

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
