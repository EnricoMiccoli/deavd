from flask import Flask
from flask import request
from flask import render_template
from deavd import * # necessary to properly unpickle

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('homepage.html', buckets=['shapes'])

@app.route('/b/<bucketname>')
def bucketpage(bucketname=None):
    try:
        bucket = loadbucket(bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    return render_template('bucketpage.html', bucket=bucket)

@app.route('/b/<bucketname>', methods=['POST'])
def bucketquery(bucketname=None):
    try:
        bucket = loadbucket(bucketname)
    except FileNotFoundError:
        return render_template('nobucketfound.html', bucketname=bucketname)
    query = parsequery(request.form['query'])
    assert len(query) > 0
    result = Bucket('result')
    try:
        result.update(bucket.query(query))
    except ValueError:
        return 'Invalid operator in query ' + query
    return render_template('bucketpage.html', bucket=result)



app.debug = True

if __name__ == '__main__':
    app.run()
