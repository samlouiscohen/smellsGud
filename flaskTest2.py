from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3 as lite
from webCrawler import getAllFoods
from contextlib import closing
from flask_mail import Mail, Message
import sys


app = Flask(__name__)
app.config.update(
DEBUG = True,
MAIL_SERVER = 'smtp.gmail.com',
MAIL_PORT=465,
MAIL_USE_SSL=True,
MAIL_USERNAME = 'leostilwell@gmail.com',
MAIL_PASSWORD = 'XXXX'
)
mail = Mail(app)
app.config.from_object(__name__)
app.database = "WhatsCookin\'.db"


food = []
food = getAllFoods()
FullLength = len(food)
length1 = len(food)

def connect_db():
	return lite.connect(app.database)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()



@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



@app.route('/')
def home():

	cur = g.db.execute('select * from entries')
	entries = [dict(food=row[1], attributes = row[2]) for row in cur.fetchall()]
	
	return render_template('index.html', entries = entries)

def refresh():
	food = []
	food = getAllFoods()
	FullLength = len(food)
	length1 = len(food)
	print("hi", file=sys.stderr)
	g.db = connect_db()
	
	g.db.execute("INSERT INTO entries(food,attributes) VALUES('chicken')")
	for x in range(0,FullLength):
		
		for y in range(0,len(food[x])):
			string1 = food[x][y][0]
			string2 = food[x][y][1][0]
			g.db.execute("INSERT INTO entries(food,attributes) VALUES(string1,string2)")
			g.db.commit()

	g.db.commit()
    
@app.route('/mail')
def send_Mail():
	#toSend = ""
	msg = Message("Mail Test",
		sender = 'leostilwell@gmail.com',
		recipients = ['slc2206@columbia.edu'])
	
	g.db = connect_db()
	cur = g.db.execute('select * from entries order by id desc')
	data = cur.fetchall()
	for row in data:
		entries = dict(food=row[1],attributes=row[2])

	toSend =', '.join("{!s}={!r}".format(key,val) for (key,val) in entries.items())

	print (toSend)

	
	msg.body = toSend
	mail.send(msg)
	return render_template('mail.html')


@app.route('/addUser', methods = ['GET','POST'])
def add_User():
	error = None
	g.db = connect_db()
	
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		preferences = request.form['preferences']
		if(g.db.execute("SELECT EXISTS(SELECT 1 from users WHERE username=username)")):
			print("hi")
			error = 'Invalid username'
			
		else:
			g.db.execute("INSERT INTO users(username,password,email,KeyWords) VALUES(username, password, email, preferences")
			#flash("You are now registered!")
			print("hi")
			return redirect('http://127.0.0.1:5000/thankyou')
	
	
	g.db.commit()
	g.db.close()
	return render_template('newuser')

@app.route('/thankyou')
def thankyou():
	return render_template('thankyou.html')


app.run()
