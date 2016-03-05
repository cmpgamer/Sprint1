import sys
reload(sys)
sys.setdefaultencoding("UTF8")

import os
import uuid
from flask import *
from flask.ext.socketio import SocketIO, emit
from flask_socketio import join_room, leave_room

import psycopg2
import psycopg2.extras


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

messages = []
users = {}


def connect_to_db():
    return psycopg2.connect('dbname=movie_reviews user=postgres password=Cmpgamer1 host=localhost')
    
loadMessagesQuery = 'SELECT username, content FROM messages INNER JOIN users ON messages.senderid = users.id WHERE messages.room_id = %s ORDER BY messages.id DESC LIMIT 10' # keep track of last 50 messages   

@socketio.on('connect', namespace='/movie')
def makeConnection():
    session['uuid'] = uuid.uuid1()
    print ('Connected')
    
@socketio.on('identify', namespace='/movie')
def on_identify(user):
    print('Identify: ' + user)
    users[session['uuid']] = {'username' : user}
    
@socketio.on('search', namespace='/movie')
def search(searchItem):
    
    print("I am here")
    
    db = connect_to_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    searchQuery = ""
    results = []
    queryResults = []
    searchTerm = '%{0}%'.format(searchItem)
        
    cur.execute(searchQuery, (searchTerm,));
    results = cur.fetchall();
    
    print(results)
    
    # for i in range(len(results)):
    #     resultsDict = {'text' : results[i]['content'], 'name' : results[i]['username']}
    #     queryResults.append(resultsDict)
        
    emit('searchResults', queryResults)
    cur.close()
    db.close()



# @app.route('/chat')
# def chat():
#     if 'username' in session:
#         return render_template('chat.html') # chat.html
#     else:
#         return render_template('index.html')


#TODO make new search functions displaying queries




@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return render_template('index.html')    
    
    
doesUserAlreadyExist = 'SELECT * FROM users WHERE username = %s LIMIT 1'
registerNewUser = "INSERT INTO users VALUES (default, %s, %s, %s, crypt(%s, gen_salt('md5'))) RETURNING users.id"
@app.route('/register', methods=['GET', 'POST'])
def register():
    redirectPage = 'index.html'
    error = ''
    if request.method == 'POST':
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        username = request.form['registerUsername']
        password = request.form['registerPassword']
        password2 = request.form['registerConfirmPassword']
        
        if username.isspace():
            error += 'Username is required.\n'
        if firstName.isspace():
            error += 'First Name is required.\n'
        if lastName.isspace():
            error += 'Last Name is required.\n'
        if password.isspace():
            error += 'Password is required.\n'
        if password2.isspace():
            error += 'Password must be entered in twice.\n'
        if password != password2:
            error += 'Passwords do not match.\n'
        
        if len(error) == 0:
            cur.execute(doesUserAlreadyExist, (username,)) # check whether user already exists
            if cur.fetchone():
                error += 'Username is already taken.\n'
            else:
                cur.execute(registerNewUser, (firstName, lastName, username, password)) # add user to database

        cur.close()
        db.close()

        if len(error) != 0:
            redirectPage = 'index.html'
            
    if len(error) != 0:
        pass
        # flash error message
        
    return render_template(redirectPage, error=error)
    
loginQuery = 'SELECT * from users WHERE username = %s AND password = crypt(%s, password)'
getRoomQuery = "SELECT *  FROM room_subscriptions WHERE user_id = %s"
@app.route('/login', methods=['GET', 'POST'])
def login():
    redirectPage = 'index.html'
    error = ''
    if request.method == 'POST':
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        username = request.form['username']
        pw = request.form['password']
      
        cur.execute(loginQuery, (username, pw))
        results = cur.fetchone()
        
        cur.close()
        db.close()
        
        if not results: # user does not exist
            error += 'Incorrect username or password.\n'
        else:
            session['username'] = results['username']
            session['id'] = results['id']
            results = []
            return redirect(url_for('chat'))
         
    if len(error) != 0:
        pass
        # flash error
        
    return render_template(redirectPage, error=error)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))
    
# start the server
if __name__ == '__main__':
        socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
