from flask import Flask, g, render_template, make_response, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, send, emit
from threading import Thread
import rethinkdb as r
from rethinkdb import RqlRuntimeError
import json
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='secret!',
    DB_HOST='db',
    DB_PORT=28015,
    DB_NAME='chat'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)





def init_db():
    conn = r.connect(app.config['DB_HOST'], app.config['DB_PORT'])
    try:
        r.db_create(app.config['DB_NAME']).run(conn)
        r.db(app.config['DB_NAME']).table_create('chats').run(conn)
        r.db(app.config['DB_NAME']).table('chats').index_create('created').run(conn)
        print 'Database setup completed. Now run the app without --setup.'
    except RqlRuntimeError:
        print 'App database already exists. Run the app without --setup.'
    finally:
        conn.close()

@app.before_request
def before_request():
    try:
        g.db_conn = r.connect(host=app.config['DB_HOST'], 
                              port=app.config['DB_PORT'], 
                              db=app.config['DB_NAME'])
    except RqlDriverError:
        abort(503, "No database connection could be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.db_conn.close()
    except AttributeError:
        pass

@app.route('/chats/', methods=['POST'])
def create_chat():
    data = json.loads(request.data)
    data['created'] = datetime.now(r.make_timezone('00:00'))
    if data.get('name') and data.get('message'):
        new_chat = r.table("chats").insert([ data ]).run(g.db_conn)
        return make_response('success!', 201)
    return make_response('invalid chat', 401)

@app.route('/', methods=['GET'])
def list_shows():
    chats = list(r.table("chats").order_by(index=r.desc('created')).run(g.db_conn))
    return render_template('chats.html', chats=chats)

def watch_chats():
    print 'Watching db for new chats!'
    conn = r.connect(host=app.config['DB_HOST'], 
                     port=app.config['DB_PORT'], 
                     db=app.config['DB_NAME'])
    feed = r.table("chats").changes().run(conn)
    for chat in feed:
        print 'emitting new chat: ', chat
        chat['new_val']['created'] = str(chat['new_val']['created'])
        socketio.emit('new_chat', chat)


if __name__ == "__main__":
    # Set up rethinkdb changefeeds before starting server
    thread = Thread(target=watch_chats)
    thread.start()
    socketio.run(app, host='0.0.0.0', port=8000)
