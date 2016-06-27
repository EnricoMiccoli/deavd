import os
import shutil
import time
import modules.deavd as deavd
import modules.owncrypto as oc
import modules.clearance as cl
from flask import Flask
from flask_scss import Scss
from flask import render_template, redirect, url_for, request, send_file, abort

app = Flask(__name__,
        static_folder='sitefiles/static',
        template_folder='sitefiles/templates',
        )
app.debug = True
app.secret_key = os.urandom(512)

Scss(app, asset_dir='sitefiles/')

BUCKETDIR = 'sitefiles/buckets/'
def loadbucket(bucketname):
    return deavd.loadbucket('%s%s/%s.bk' % (BUCKETDIR, bucketname, bucketname))

BUCKET_CLEARANCES = {'shapes': '', 'restricted': 'omega'}

@app.route('/theta')
@cl.require_clearance('theta')
def theta():
    return 'this is theta secret'

@app.route('/delta')
@cl.require_clearance('delta')
def delta():
    return 'this is a delta secret'

@app.route('/test')
def testpage():
    try:
        return render_template('message.html', title='Credential Check', message='You are ' +
                cl.user()['username'] +
                ' and you are ' +
                'not ' * int(not cl.user()['authenticated']) +
                'authenticated ' +
                'with ' * int(cl.user()['authenticated']) +
                ', '.join([x for x in cl.userdb[cl.user()['username']]['clearances']])
                )
    except KeyError:
        return render_template('message.html',
                title='Not logged in',
                message='You are not logged in on this server.')

@app.route('/login')
def loginpage():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login(referrer=None):
    sessionid = cl.assignid()
    password = request.form['password']
    username = request.form['username']
    try:
        if oc.authenticate(password, cl.userdb[username]['password']):
            cl.user()['username'] = username
            cl.user()['authenticated'] = 1
            return redirect(request.form['referrer'], 302)
    except KeyError:
        pass
    return render_template('message.html', title="Invalid credentials")

@app.route('/logout')
def logoutpage():
    cl.mastersession.pop(session['id'])
    return render_template('message.html', title="Logged out", message="You have succesfully logged out")

@app.route('/')
def homepage():
    bucketnames = os.listdir('sitefiles/buckets')
    return render_template('homepage.html', buckets=bucketnames)

@app.route('/b/<bucketname>')
@cl.bucket_clearance(BUCKET_CLEARANCES)
def bucketpage(bucketname=None):
    try:
        bucket = loadbucket(bucketname)
        fbp = os.path.splitext(bucket.path)[0] # Father bucket path
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    return render_template('bucketpage.html', bucket=bucket, fbp=fbp)

@app.route('/b/<bucketname>', methods=['POST'])
@cl.bucket_clearance(BUCKET_CLEARANCES)
def bucketquery(bucketname=None):
    try:
        bucket = loadbucket(bucketname)
        fbp = os.path.splitext(bucket.path)[0] # Father bucket path
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)

    stringquery = request.form['query']
    if not stringquery: # checks for empty query
        return render_template('bucketpage.html', bucket=bucket, prevsearch='', fbp=fbp)
    else:
        query = deavd.parsequery(stringquery)
        result = deavd.Bucket('Results of your query')
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
@cl.bucket_clearance(BUCKET_CLEARANCES)
def entpage(bucketname=None, entkey=None):
    try:
        bucket = loadbucket(bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    try:
        entity = bucket[entkey]
    except KeyError:
        return render_template('noentityfound.html', bucketname=bucketname, entityname=entityname) 
    return render_template('entitypage.html', bucketname=bucket.name, fbp=bucketname, ent=entity)

@app.route('/blobs/<bucketname>/<imagename>')
@cl.bucket_clearance(BUCKET_CLEARANCES)
def serve_image(bucketname=None, imagename=None):
    return send_file('sitefiles/buckets/%s/%s' % (bucketname, imagename), as_attachment=False)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('message.html',
            title="Page not found",
            message="The resource you requested is not present on the server.",
            link=[url_for('homepage'), "Go back home"]), 404

if __name__ == '__main__':
    app.run()
