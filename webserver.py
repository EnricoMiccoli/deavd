import os
import time
import logging
import modules.deavd as deavd
import modules.owncrypto as oc
import modules.clearance as cl
import modules.log
from  modules.config import conf
from flask import Flask
from flask_scss import Scss
from flask_compress import Compress
from flask import render_template, redirect, url_for, request, send_file, abort, session

app = Flask(__name__,
        static_folder=conf['staticdir'],
        template_folder=conf['templatedir'],
        )
app.debug = conf['debug']
app.secret_key = os.urandom(conf['secretlength'])
Compress(app)

Scss(app, asset_dir=conf['scssdir'], static_dir=conf['staticdir'] + '/')
# I'm not sure about that added slash, but it's necessary

BUCKET_CLEARANCES = conf['bucketclear']

@app.after_request
def afterrequest(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Server"] = ""
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self' fonts.googleapis.com; frame-ancestor 'none'; font-src fonts.gstatic.com;"
    return response

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
    ip = request.environ['REMOTE_ADDR']
    cl.user()['ip'] = ip
    try:
        if oc.authenticate(password, cl.userdb[username]['password']):
            cl.user()['username'] = username
            cl.user()['authenticated'] = 1
            logging.info('%s, %s login' % (ip, username))
            return redirect(request.form['referrer'], 302)
    except KeyError:
        oc.authenticate(password, cl.dummy)
    cl.user()['fails'] += 1
    if cl.user()['fails'] == 5:
        logging.warning(user()['ip'] + ' 5 wrong login attemps') 
    return render_template('message.html', title="Invalid credentials")

@app.route('/logout')
def logoutpage():
    cl.mastersession.pop(session['id']) #FIXME
    return render_template('message.html', title="Logged out", message="You have succesfully logged out")

@app.route('/')
def homepage():
    bucketnames = os.listdir('sitefiles/buckets')
    return render_template('homepage.html', buckets=bucketnames)

@app.route('/b/<bucketname>/<int:page>')
@cl.bucket_clearance(BUCKET_CLEARANCES['read'])
def bucketpage(bucketname=None, page=0):
    try:
        bucket = deavd.loadbucket(bucketname)
        fbp = os.path.splitext(bucket.path)[0] # Father bucket path
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    epp = conf['entsperpage']
    try:
        qks = session['querykeys']
    except KeyError:
        # No previous session
        session['querykeys'] = []
        qks = []
    if qks:
        if qks == [None]:
            # No results
            session['querykeys'] = []
            return render_template(
                    'bucketpage.html',
                    bucket=bucket,
                    fbp=fbp,
                    empty=True,
                    )
        else:
            # Some results
            keys = qks[page * epp: (page + 1) * epp]
            totalpages = len(qks) // epp + (len(qks) % epp != 0) * 1
    else:
        # Query is empty: show all
        keys = list(bucket.keys())[page * epp: (page + 1) * epp]
        totalpages = len(bucket) // epp + (len(bucket) % epp != 0) * 1
    return render_template(
            'bucketpage.html',
            bucket=bucket,
            fbp=fbp,
            keys=keys,
            totalpages=range(totalpages),
            current=page,
            )

@app.route('/b/<bucketname>/<int:page>', methods=['POST'])
@cl.bucket_clearance(BUCKET_CLEARANCES['read'])
def bucketquery(bucketname=None, page=0):
    try:
        bucket = deavd.loadbucket(bucketname)
        fbp = os.path.splitext(bucket.path)[0] # Father bucket path
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)

    stringquery = request.form['query']
    if stringquery and not stringquery.isspace():
        query = deavd.parsequery(stringquery)
        goodkeys = list(bucket.query(query))
        if goodkeys:
            session['querykeys'] = goodkeys
        else:
            session['querykeys'] = [None]
    else:
        session['querykeys'] = []
    return redirect('/b/%s/0' % bucketname)

@app.route('/b/<bucketname>/<entkey>')
@cl.bucket_clearance(BUCKET_CLEARANCES['read'])
def entpage(bucketname=None, entkey=None):
    try:
        bucket = deavd.loadbucket(bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    try:
        entity = bucket[entkey]
    except KeyError:
        return render_template('noentityfound.html', bucketname=bucketname, entityname=entityname)
    return render_template('entitypage.html', bucketname=bucket.name, fbp=bucketname, ent=entity, bucketurl='/b/%s/0' % bucketname)

@app.route('/b/<bucketname>/<entkey>', methods=['POST'])
@cl.bucket_clearance(BUCKET_CLEARANCES['write'])
def addtag(bucketname=None, entkey=None):
    try:
        tagname = request.form['tagname']
        bucket = deavd.loadbucket(bucketname)
        bucket[entkey].addtag(deavd.Tag(tagname))
        bucket.dump()
        logging.info('%s, %s tagged %s/%s %s' % (cl.user()['ip'], cl.user()['username'], bucketname, entkey, tagname))
    except (FileNotFoundError, KeyError):
        logging.warning('POST at nonexisting %s/%s' % (bucketname, entkey))
        return abort(404)
    return redirect('/b/%s/%s' % (bucketname, entkey))

@app.route('/blobs/<use>/<bucketname>/<filename>')
@cl.bucket_clearance(BUCKET_CLEARANCES['read'])
def serve_image(bucketname=None, filename=None, use=None):
    ext = os.path.splitext(filename)[1][1:]
    if use == 'preview':
        if ext in conf['imgexts']:
            return send_file('sitefiles/buckets/%s/%s' % (bucketname, filename),
                    as_attachment=False)
        elif ext in conf['txtexts']:
            return send_file('sitefiles/icons/text.svg', as_attachment=False)
        else:
            logging.error('Forbidden filetype %s' % ext)
    elif use == 'download':
        if ext in conf['imgexts']:
            return send_file('sitefiles/buckets/%s/%s' % (bucketname, filename),
                    as_attachment=True)
        elif ext in conf['txtexts']:
            return send_file('sitefiles/buckets/%s/%s' % (bucketname, filename),
                    as_attachment=True)
        else:
            logging.error('Forbidden filetype %s' % ext)
    else:
        logging.warning('Unknown usecase %s' % use)
        return abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('message.html',
            title="Page not found",
            message="The resource you requested is not present on the server.",
            link=[url_for('homepage'), "Go back home"]), 404

if __name__ == '__main__':
    logging.debug('app starting')
    app.run(host=conf['host'], port=conf['port'])
