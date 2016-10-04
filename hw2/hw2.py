# !/usr/bin python
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort,\
                  render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'hw2.db'),
    SECRET_KEY='development key',
    USERNAME='hw2',
    PASSWORD='password'
))
app.config.from_envvar('HW2_SETTINGS', silent=True)

def connectToDB():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row

    return rv

def initDB():
    db = getDB()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initDBCommand():
    initDB()
    print "DB initialized"

def getDB():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connectToDB()

    return g.sqlite_db

@app.teardown_appcontext
def closeDB(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def showEntries():
    db      = getDB()
    cur     = db.execute('select name from entries order by id desc')
    entries = cur.fetchall()

    return render_template('showEntries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    db = getDB()
    db.execute('insert into entries (name) values (?)',
               [request.form['name'],])
    db.commit()
    flash('Post successful')
    return redirect(url_for('showEntries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid.password'
        else:
            session['logged_in'] = True
            flash('Successfuly logged in')
            return redirect(url_for('showEntries'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Successfully logged out')

    return redirect(url_for('showEntries'))
