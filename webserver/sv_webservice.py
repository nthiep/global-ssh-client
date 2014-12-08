#!/usr/bin/env python
#
# Name:     Global SSH Webservice
# Description:  help connect ssh between client via return public ip and ramdom port.
#               use websocket and HTTP server.
# project 2
# Server:   cloud platform heroku
#
# Author:   Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time:     2014/10
# Requirements:  view requirements.txt
#

import sys, time, os, datetime, hashlib, random
from functools import wraps
from flask import Flask, request, Response, json, render_template, session, redirect, url_for, render_template, flash
from sv_user import User
app = Flask(__name__)
app.config['SECRET_KEY'] = "global-ssh-6173b812b1d07e2306f37246d49d147ea601305b"
app.config['DEBUG'] = True
u = User()
def request_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']

def check_auth(username, password):
    if u.check(username) and u.auth(username, password):
        return True
    return False

def authenticate():
    return Response('You login with wrong credentials', 401)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request_json():
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash("you must login first.")
                return redirect(url_for('api_login'))
        else:
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                auth = json.loads(request.headers.get('authorization'))
                mac = auth["mac"]
                token = auth["token"]
                tk = u.check_token(mac, token)
                if not tk:
                    return authenticate()
                session['logged_in'] = True
                session['username'] = tk["user"]
                return f(*args, **kwargs)
    return decorated

def register(user, pswd):
    if u.check(user):
        return Response('The username has already exist! please choose another one', 400)
    u.register(user, pswd)
    return Response('Congratulations %s your registration has been successful!' % user, 200)

def login(mac, host, user, pswd):
    if not check_auth(user, pswd):
        return authenticate()
    code = random.getrandbits(128)
    token = hashlib.sha1(str(code)).hexdigest()
    u.add_token(mac, host, token, user)
    session['logged_in'] = True
    session['username'] = user
    log = "generate new token"
    u.addlog(user, mac, log)
    return token
    
def user(user):
    return u.user(user)
def machines(user):
    res = []
    data = u.machine(user)
    for o in data:
        res.append({'host': o["host"], 'mac' : o["mac"]})
    return res
def onlines(user):
    res = []
    data = u.onlines(user)
    for o in data:
        res.append({'host': o["host"], 'mac' : o["mac"]})
    return res
def logs(user):
    res = []
    data = u.logs(user)
    for l in data:
        res.append({'time': l["time"], 'mac':  l["mac"], 'log' : l["log"]})
    return res

def logout(user):
    for u in lsclient:
        if u.name == user:
            u.connection.close()
            lsclient.remove(u)
            return "you has logout"
    return "you are not login"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request_json():
        return "Welcome!\nGlobal SSH Webservice\n%s" % str(datetime.datetime.now())
    else:
        return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def api_register():
    if request_json():
        if request.json["username"] and request.json["password"]:
            return register(request.json["username"], request.json["password"])
        return "bad request"
    else:
        error = None
        if 'logged_in' in session:
            return redirect(url_for('index'))
        if request.method == 'POST':
            error = register(request.form['username'], hashlib.sha1(request.form['password']).hexdigest())
        return render_template('register.html', error = error)
@app.route('/login', methods=['GET', 'POST'])
def api_login():
    if request_json():       
        auth = json.loads(request.headers.get('authorization'))
        mac = auth["mac"]
        host = auth["host"]
        user = auth["username"]
        pswd = auth["password"]
        return login(mac, host, user, pswd)
    else:
        error = None
        if 'logged_in' in session:
            return redirect(url_for('index'))
        if request.method == 'POST':
            if not check_auth(request.form['username'], hashlib.sha1(request.form['password']).hexdigest()):
                error = "wrong username or password"
            else:
                session['logged_in'] = True
                session['username'] = request.form['username']
                return redirect(url_for('index'))
        return render_template('login.html', error = error)


@app.route('/user/<username>', methods=['GET', 'POST'])
@requires_auth
def api_user(username):
    return render_template('user.html', info = user(username), user = username )

@app.route('/onlines', methods=['GET', 'POST'])
@requires_auth
def api_online():
    if request_json():
        return json.dumps(onlines(session['username']))
    else:
        return render_template('content.html', data = onlines(session['username']), page = "onlines")
@app.route('/machines', methods=['GET', 'POST'])
@requires_auth
def api_machines():
    if request_json():
        return json.dumps(machine(session['username']))
    else:
        return render_template('content.html', data = machines(session['username']), page = "machines")
@app.route('/logs', methods=['GET', 'POST'])
@requires_auth
def api_logs():
    if request_json():
        print logs(session['username'])
        return json.dumps(logs(session['username']))
    else:        
        return render_template('content.html', data = logs(session['username']), page = "logs")

@app.route('/logout', methods=['GET', 'POST'])
@requires_auth
def api_logout():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        return logout(auth.username)
    else:
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('logged out')
        return redirect(url_for('index'))
@app.route('/about', methods=['GET'])
def api_about():
    return redirect("https://gssh.github.io", code=302)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run("",5000)