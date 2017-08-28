from flask import Flask, render_template, request, Response, redirect
import psycopg2
import psycopg2.extras
import datetime
import os
from functools import wraps
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl

app = Flask(__name__)

connection_string = os.environ['DATABASE_URL']

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == os.environ['USERNAME'] and password == os.environ['PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def hello_world():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM temperature ORDER BY reading_date DESC LIMIT 5')
    records = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('index.html', temperature=44, )


@app.route('/info')
def about():
    records = ['12', '23', '43', '29', '59']
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM temperature ORDER BY reading_date DESC')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM temperature ORDER BY temperature DESC LIMIT 1')
    highest = cursor.fetchall()
    max = highest[0]

    cursor.execute('SELECT * FROM temperature ORDER BY temperature ASC LIMIT 1')
    lowest = cursor.fetchall()
    min = lowest[0]

    # TODO read the lowest temperature

    conn.commit()
    conn.close()
    return render_template('info.html', my_name='Odin', team_name='Box', project_name='SmartRoom', records=records,
                           highest=max, lowest=min, )


@app.route('/money')
def me():
    return render_template('sponsors.html')

@app.route('/form')
@requires_auth
def posture():
     return render_template('formation.html')

@app.route('/handle', methods=['POST'])
@requires_auth
def grab():
    temperature = request.form['temperature']
    current_date = datetime.datetime.now()
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = 'INSERT INTO temperature (reading_date, temperature)  VALUES (\'%s\', %s)' % (current_date, temperature)
    cursor.execute(query)
    conn.commit()
    conn.close()
    return redirect('/info')
    return query

@app.route('/led', methods=['POST'])
def led():
    device_id = os.environ['DEVICE_ID']
    access_token = os.environ['ACCESS_TOKEN']
    url = "https://api.particle.io/v1/devices/%s/led?access_token=%s" % (device_id, access_token)
    arg = request.form['arg']
    post_fields = {'arg': arg}
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    req = Request(url, urlencode(post_fields).encode())
    urlopen(req, context=gcontext)
    return url


@app.route('/ledstate')
def ledstate():
    device_id = os.environ['DEVICE_ID']
    access_token = os.environ['ACCESS_TOKEN']
    url = "https://api.particle.io/v1/devices/%s/ledstate?access_token=%s" % (device_id, access_token)
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    return urlopen(url, context=gcontext).read()

@app.template_filter('format_date')
def reverse_filter(record_date):
    return record_date.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/apihandle', methods=['POST'])
@requires_auth
def grab():
    temperature = request.form['temperature']
    current_date = datetime.datetime.now()
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = 'INSERT INTO temperature (reading_date, temperature)  VALUES (\'%s\', %s)' % (current_date, temperature)
    cursor.execute(query)
    conn.commit()
    conn.close()
    return "OK"



if __name__ == '__main__':
    app.run()


