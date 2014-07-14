import json #psycopg2
import sys,os,os.path

from flask import Flask, jsonify, abort, make_response, g, abort, Response
from flask import request, session, redirect, url_for, render_template, flash

from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators

sys.path.append("../..")

import urllib, urllib2, cookielib, uuid, datetime
from datetime import timedelta
from bs4 import BeautifulSoup 
from functools import wraps

from forms import LoginForm

from writeSQL import (questions_sql, get_api_token_expiration, get_api_token,
                      insert_api_token, dump_sql, state_sql, question_id_sql,
                      question_name_sql, state_question_id_sql, state_question_sql)
import config

uuid._uuid_generate_time = None
uuid._uuid_generate_random = None

app = Flask(__name__)
app.secret_key = config.s_key

#TODO: ADD LOGIN REQ AGAIN, SET SETTINGS
if __name__ == "__main__" and __package__ is None:
    __package__ = "ogea.api"

def api_login_required(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        if request.headers.get('accept', None) == 'application/json':
            if not validate_token(request.args.get('token')):
                return json.dumps({'error': 'Invalid token, please login to retrieve a valid token.'})
        else:
            #if not (g.user and g.user.is_authenticated()):
            if session.get('logged_in', False) == False:
                flash('You must be logged in to access this resource.')
                return redirect(url_for('login', next=request.url))

        return view(*args, **kwargs)

    return decorated_view

def validate_token(token):
    """
    Checks if the token is in the database, and that the 
    """
    expiration = get_api_token_expiration(token)

    if expiration:
        expiration = expiration[0]['expiration']
    else:
        return False

    if not expiration or expiration >= datetime.date.today():
        return True

    return False

def login_to_noisite(username, password):
    """
    In order to login to the API, the user must have an existing
    account with neworganizing.com.  This function passes along the
    provided username and password to the NOI login form, taking
    CSRF into account, and if the resulting redirect is not back
    to the login form, then the authentication was successful.

    TODO: Enable the neworganizing.com site to react appropriately
    to application/json requests, and return a proper authentication
    confirmation.
    """

    if config.DEBUG:
        return True

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    login_url = 'http://{0}/accounts/login/'.format(config.NOISITE_DOMAIN)

    request = urllib2.Request(login_url)
    request.add_header('User-Agent', 'Browser')
 
    response = urllib2.urlopen(request)
    html = response.read()

    doc = BeautifulSoup(html)

    csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
    csrf_token = csrf_input['value']

    params = urllib.urlencode(dict(username=username, password=password, csrfmiddlewaretoken = csrf_token))
    request.data = params

    response = urllib2.urlopen(request)

    if response.geturl() == login_url:
        return False
    else:
        return True

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(csrf_enabled=False)

    if session.get('logged_in', False) == True:
        return redirect(url_for('main'))

    if request.form:
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        logged_in = login_to_noisite(username, password)

        if logged_in:
            accept_header = request.headers.get('accept', None)
            if not accept_header:
                accept_header = request.headers.get('Accept', None)

            if accept_header and accept_header == 'application/json':
                # Check if token already exists (i.e. permanent tokens)
                token = get_api_token(username)

                if not token:
                    token = uuid.uuid4()
                    expiration = datetime.date.today()+timedelta(days=1)
                    insert_api_token(username, token, expiration)

                return json.dumps({'logged_in':'true', 'token':str(token)})
            else:
                session['logged_in'] = True
                return redirect(request.args.get('next') or url_for('main'))
        else:
            if request.headers['accept'] == 'application/json':
                return json.dumps({'logged_in':'false'})
            else:
                flash('Failed to login.')

    return render_template('login.html', form=form, title = 'Login')

@app.route('/logout')
def logout():    
    flash('You have been logged out')
    session['logged_in'] = False

    return redirect(url_for('main'))

@app.route('/')
def main():
    if session.get('logged_in', False) == False:
       flash('You are not logged in')
    return render_template('main.html')

@app.route('/questions/', methods = ['GET'])
@api_login_required
def get_questions():
    return json.dumps(questions_sql())

@app.route('/question/<int:q_id>', methods = ['GET'])
@api_login_required
def get_question_id(q_id):
    return json.dumps(question_id_sql(q_id))

@app.route('/question/<path:ques>', methods = ['GET'])
@api_login_required
def get_question(ques):
    ques = urllib.unquote(ques)
    return json.dumps(question_name_sql(ques))

@app.route('/<state>/<int:q_id>', methods = ['GET'])
@api_login_required
def get_state_question_id(state, q_id):
    return json.dumps(state_question_id_sql(state, q_id))

@app.route('/<state>/<path:ques>', methods = ['GET'])
@api_login_required
def get_state_question(state, ques):
    ques = urllib.unquote(ques)
    return json.dumps(state_question_sql(state, ques))

@app.route('/<state>', methods = ['GET'])
@api_login_required
def get_state(state):
    return json.dumps(state_sql(str(state)))

@app.route('/dump', methods = ['GET'])
@api_login_required
def dump():
    return json.dumps(dump_sql())

@app.errorhandler(401)
def handler_401(error):
    return Response('Error: Unauthorized API Access Attempt', 401, {'WWWAuthenticate':'Basic realm="Login Required"'})

#topic/subtopic at some later date

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(config.API_LOG_PATH+'ogeapi.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run(debug=config.DEBUG)
