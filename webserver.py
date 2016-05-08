from flask import Flask
from flask import request
from flask import render_template
from flask.ext.scss import Scss
from deavd import * # necessary to properly unpickle

app = Flask(__name__)
app.debug = True
Scss(app, asset_dir='./')

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

    stringquery = request.form['query']
    if not stringquery: # checks for empty query
        return render_template('bucketpage.html', bucket=bucket, prevsearch='')
    else:
        query = parsequery(stringquery)
        assert len(query) > 0

        result = Bucket('Results of your query')
        try:
            result.update(bucket.query(query))
        except ValueError:
            return 'Invalid operator in query ' + query

        # check if empty
        if result:
            return render_template('bucketpage.html', bucket=result, prevsearch=stringquery)
        else: 
            return render_template('bucketpage.html', bucket=result, prevsearch=stringquery, empty=True)



if __name__ == '__main__':
    app.run()
