from flask import Flask
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


app.debug = True

if __name__ == '__main__':
    app.run()
