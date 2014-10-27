import sys, time, os, datetime, hashlib, random
from functools import wraps
from flask import Flask, request, Response, json, render_template, session, redirect, url_for, render_template, flash
from flask_sockets import Sockets
from sv_user import User
global lsclient
lsclient = []
app = Flask(__name__)
app.secret_key = "1234567890"
app.debug = 'DEBUG' in os.environ
app.config['DEBUG'] = True
app.config['DEBUG'] = os.environ.get('DEBUG', False)
sockets = Sockets(app)

class Client(object):
    def __init__(self, name, addr, localadd, connection):
        self.name = name
        self.addr = addr
        self.local = localadd
        self.connection = connection

def request_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']

def check_auth(username, password):
    u = User(username)
    if u.check() and u.auth(password):
        return True
    return False

def authenticate():
    return Response('You login with wrong credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request_json():
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash("you must login first.")
                return redirect(url_for('api_login'))
        return f(*args, **kwargs)
    return decorated
def getip():
    fwd = request.environ.get('HTTP_X_FORWARDED_FOR', None)
    if fwd is None:
        return request.environ.get('REMOTE_ADDR')
    fwd = fwd.split(',')[0]
    return fwd
def register(user, pswd):
    u = User(user)
    if u.check():
        return "The username has already exist! please choose another one"
    u.register(pswd)
    u.addlogs(str(datetime.datetime.now()), 'registered successful at %s' % getip())
    return "Congratulations your registration has been successful! Now you can use services"
def checklogin(user):
    for u in lsclient:
        if u.name == user:
            return True
    return False
def login(user, pswd):
    u = User(user)
    ip = getip()
    if checklogin(user):
        u.addlogs(str(datetime.datetime.now()), 'login error: duplicate login at %s' % ip)
        return json.dumps({"error": "you has login another machine"})
    return json.dumps({"address": ip})

def user(user, peer):
    res = []
    u = User(user)
    p = User(peer)
    if p.check():
        if p.checkfriend(user):
            data = p.downloadkey()
            if data:
                key = data['key']
            else:
                key = 'No public key'

            if checklogin(peer):
                res.append({"status": "online", "key": key})
                return res
            else:
                res.append({"status": "offline", "key": key})
                return res
    res.append({"error": "not found or not your friend"})
    return res


def conninfo(user, port, peer, hashcode):
    addp = None
    for p in lsclient:
        if p.name == peer:
            addp = p.addr
    for u in lsclient:
        if u.name == user:
            return json.dumps({"status": 200, "hashcode" : hashcode, 'me': addp, 'port': port, "peer" : peer, "address" : u.addr, "localadd" : u.local})
    return None

def connect(user, peer):
    u = User(user)
    f = User(peer)
    if not u.checkfriend(peer) or not checklogin(peer):        
        u.addlogs(str(datetime.datetime.now()), 'connect error: unknown friend or not online %s at %s' % (peer, getip()))
        return json.dumps({"status": 404, 'response' : '%s is not found or not online' % peer})
    code = random.getrandbits(128)
    port = random.randrange(20000, 65000)
    hashcode = hashlib.sha1(str(code)).hexdigest()
    ju = conninfo(user, port, peer, hashcode)
    jp = conninfo(peer, port, user, hashcode)
    for p in lsclient:
        if p.name == peer:
            p.connection.send(ju)
            u.addlogs(str(datetime.datetime.now()), 'connecting to %s(%s) at %s' % (peer, p.addr, getip()))
            f.addlogs(str(datetime.datetime.now()), 'connecting from %s(%s) at %s' % (user, getip(), p.addr))  
    return jp
def upload(user, key):
    u = User(user)
    u.uploadkey(key)
    u.addlogs(str(datetime.datetime.now()), 'upload public key at %s' % getip())
    return "upload complete"

def addkey(user, peer):
    u = User(user)
    p = User(peer)
    res = []
    if p.check() and u.checkfriend(peer):
        key = p.downloadkey()
        if key is None:
            res.append({"error": "no key found"})
            return res
        u.addlogs(str(datetime.datetime.now()), 'add public key of %s at %s' % (peer, getip()))
        res.append({"key": key['key']})
        return res
    res.append({"error": "friend not found"})
    return res

def friends(user):
    u = User(user)
    res = []
    data1, data2 = u.lsfriend()
    if data1.count() == 0 and data2.count() == 0:
        res.append({"error": "no friend has found"})
        return res
    for f in data1:
        if checklogin(f["friend"]):
            res.append({'friend': f["friend"], 'status' : "online"})
        else:
            res.append({'friend': f["friend"], 'status' : "offline"})
    for f in data2:
        if checklogin(f["user"]):
            res.append({'friend': f["user"], 'status' : "online"})
        else:
            res.append({'friend': f["user"], 'status' : "offline"})
    return res
def onlines(user):
    u = User(user)
    res = []
    data1, data2 = u.lsfriend()
    if data1.count() == 0 and data2.count() == 0:
        res.append({"error": "no friend has found"})
        return res
    for f in data1:
        if checklogin(f["friend"]):
            res.append({'friend': f["friend"], 'status' : "online"})
    for f in data2:
        if checklogin(f["user"]):
            res.append({'friend': f["user"], 'status' : "online"})
    return res
def logs(user):
    u = User(user)
    res = []
    data = u.logs()
    if data.count() == 0:
        res.append({"error": "no logs has found"})
        return res
    for f in data:
        res.append({'time': f["time"], 'logs' : f["logs"]})
    return res
def friendrq(user):
    u = User(user)
    data = u.lsfriendrq()
    res = []
    if data.count() == 0:
        res.append({"error": "no friend request has found"})
        return res
    for f in data:
        res.append({'request': f["request"], 'time': f["time"]})
    return res
def add_friend(user, peer):
    u = User(user)
    p = User(peer)
    if p.check():
        if p.checkfriend(user):
            return "%s is your friend" % peer
        if p.checkfriendrq(user):       
            return "you had send request befor"
        p.addfiendrq(user, str(datetime.datetime.now()))        
        u.addlogs(str(datetime.datetime.now()), 'make friend: send request to %s at %s' % (peer, getip()))     
        return "add friend request has send"
    return "user you add not found"
def accept(user, peer):
    u = User(user)
    if u.checkfriendrq(peer) and not u.checkfriend(peer):
        u.addfriend(peer)        
        u.addlogs(str(datetime.datetime.now()), 'make friend: accept friend request from %s at %s' % (peer, getip()))     
        return "you has add friend %s" % peer
    return "%s is you friend or not have request of this user" % peer
def denied(user, peer):
    u = User(user)
    if u.checkfriendrq(peer):
        u.rmfriendrq(peer)
        u.addlogs(str(datetime.datetime.now()), 'make friend: denied request from %s at %s' % (peer, getip()))     
        return "request friend of %s have been remove" % peer
    return "you not have request of this friend"
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
        info = None
        if 'logged_in' in session:
            if checklogin(session['username']):
                for u in lsclient:
                    if u.name == session['username']:
                        info = 'online at %s' % u.addr
            else:
                info = 'offline'
        return render_template('index.html', info = info)
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
        auth = request.authorization
        user = auth.username
        pswd = auth.password
        if not check_auth(user, pswd):
            return authenticate()
        return login(user, pswd)
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
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        return json.dumps(user(auth.username, username))
    else:
        return render_template('user.html', info = user(session['username'], username), user = username)

@app.route('/connect', methods=['GET', 'POST'])
@requires_auth
def api_connect():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        if request.json['peer']:
            return connect(auth.username, request.json['peer'])
        else:
            return "bad request"
    else:
        return "connect page"

@app.route('/uploadkey', methods=['GET', 'POST'])
@requires_auth
def api_uploadkey():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        if request.json['key']:
            return upload(auth.username, request.json['key'])
        else:
            return "bad request"
    else:
        return "uploadkey page"


@app.route('/addkey', methods=['GET', 'POST'])
@requires_auth
def api_addkey():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        if request.json['peer']:
            return json.dumps(addkey(auth.username, request.json['peer']))
    else:
        return "addkey page"

@app.route('/friends', methods=['GET', 'POST'])
@requires_auth
def api_friend():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        return json.dumps(friends(auth.username))
    else:
        return render_template('content.html', data = friends(session['username']), page = "friends")
@app.route('/onlines', methods=['GET', 'POST'])
@requires_auth
def api_online():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        return json.dumps(onlines(auth.username))
    else:
        return render_template('content.html', data = onlines(session['username']), page = "onlines")
@app.route('/logs', methods=['GET', 'POST'])
@requires_auth
def api_logs():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        return json.dumps(logs(auth.username))
    else:
        
        return render_template('content.html', data = logs(session['username']), page = "logs")
@app.route('/friendrq', methods=['GET', 'POST'])
@requires_auth
def api_friendrq():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        return json.dumps(friendrq(auth.username))
    else:
        return render_template('content.html', data = friendrq(session['username']), page = "friendrq")

@app.route('/add', methods=['GET', 'POST'])
@requires_auth
def api_addfriend():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        if request.json["peer"]:
            return add_friend(auth.username, request.json["peer"])
        else:
            return "bad request"
    else:
        rs = None
        if request.method == 'POST' and request.form['peer']:
            rs = add_friend(session['username'], request.form['peer'])
            return render_template('addfriend.html', result = rs)
        return render_template('addfriend.html', result = rs)

@app.route('/accept', methods=['GET', 'POST'])
@requires_auth
def api_accept():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        if request.json["peer"]:
            return accept(auth.username, request.json["peer"])
        else:
            return "bad request"
    else:
        if request.method == 'POST' and request.form['peer']:
            accept(session['username'], request.form['peer'])
            return redirect(url_for('api_friendrq'))
        return "you must choice peer"
@app.route('/denied', methods=['GET', 'POST'])
@requires_auth
def api_denied():
    if request_json():
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            return authenticate()
        if request.json["peer"]:
            return denied(auth.username, request.json["peer"])
        else:
            return "bad request"
    else:
        if request.method == 'POST' and request.form['peer']:
            denied(session['username'], request.form['peer'])
            return redirect(url_for('api_friendrq'))
        return "you must choice peer"
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
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@sockets.route('/socklogin')
def sock_login(ws):
    message = ws.receive()
    data = json.loads(message)
    if check_auth(data['username'], data['password']):
        cl = Client(data['username'], data['address'], data['localadd'], ws)
        lsclient.append(cl)
        print "New connection started for %s" % data['address']
        u = User(data['username'])
        u.addlogs(str(datetime.datetime.now()), 'logged in at %s' % data['address'])
        ws.send("ok")
        while True:
            time.sleep(20)
            ws.send("ok")
        ws.close()
        lsclient.remove(cl)        

@sockets.route('/sock')
def sock(ws):
    while True:
        time.sleep(10)
        ws.send("ok")
    ws.close()