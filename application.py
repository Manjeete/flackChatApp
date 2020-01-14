import os

from flask import Flask,session,render_template,request,url_for,redirect,flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit ,join_room, send


app = Flask(__name__)
#
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# set up database in local storage 
DATABASE_URL="postgres://postgres:manjeet@localhost:5432/flack"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# validation for login
@app.route('/',methods=['GET','POST'])
def login():
	if request.method=="GET":
		return render_template("login.html")
	else:	
		username=request.form.get("username")
		password=request.form.get("password")
		query=db.execute("SELECT * FROM user_info WHERE username=:username AND password=:password",
		{"username":username,"password":password}).fetchall()
		for q in query:
			if q.username==username and q.password==password:
				session['logged_in'] = True
				session['username'] = q.username
				return redirect('/index')
		flash("Username or Password are Incorrect")							
		return redirect("/")

# validation for signup
@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method=="GET":
		return render_template("signup.html")
	else:	
		username=request.form.get("username")
		email=request.form.get("email")
		password=request.form.get("password")
		confirm_password=request.form.get("confirm_password")
		check_mail_and_username = db.execute("SELECT email,username FROM user_info WHERE email= :email OR username=:username",
			{"email":email,"username":username}).fetchone()
		if check_mail_and_username is None:
			if password == confirm_password:
				db.execute("INSERT INTO user_info(username,email,password) VALUES(:username,:email,:password)",
					{"username":username,"email":email,"password":password})
				db.commit()
				db.close()
				return redirect('/')
			else:
				flash("Password does not match")
				return redirect(request.url)
		flash( "Sorry Email or password is already taken")
		return redirect(request.url)					
		
# # home page of the website named index
@app.route('/index',methods=['GET','POST'])
def index():
	if request.method=="GET":
		if 'logged_in' in session:
			result=db.execute("SELECT * FROM channel").fetchall()
			cName="General"
			cDescription="This a flacks official room"
			return render_template("index.html",username=session['username'], result=result,cName=cName,cDescription=cDescription)
		flash("please login first")
		return redirect('/')	
			

@app.route('/create',methods=["POST"])
def create():
	channel=request.form.get('channel')
	description=request.form.get('description')
	db.execute("INSERT INTO channel(channel_name,channel_decription) VALUES(:channel,:description)",
		{"channel":channel,"description":description})
	db.commit()
	db.close()	
	return redirect(url_for('index'))

@app.route('/channel',methods=["GET","POST"])
def channel():
	if request.method=="GET":
		if 'logged_in' in session:
			result=db.execute("SELECT * FROM channel").fetchall()	
			return redirect(url_for('show_channel',channelName="General"))
	flash("please login first")
	return redirect('/')

@app.route('/channel/<string:channelName>')
def show_channel(channelName):
	cName=''.join(db.execute("SELECT channel_name FROM channel WHERE channel_name=:channelName",
		{"channelName":channelName}).fetchone())
	cDescription=''.join(db.execute("SELECT channel_decription FROM channel WHERE channel_name=:channelName",
		{"channelName":channelName}).fetchone())
	result=db.execute("SELECT * FROM channel").fetchall()
	Cmessages=db.execute("SELECT * FROM message_table WHERE room=:channelName",
		{"channelName":channelName}).fetchone()
	print(Cmessages)		
	return render_template('index.html',username=session['username'],Cmessages=Cmessages,result=result,cName=cName,cDescription=cDescription)

@socketio.on("show message")
def Show_message(data):
	message = data['message']
	room = data['room']
	username =data['username']
	from datetime import datetime
	now = datetime.now()
	tima = now.strftime("%I:%M:%S")
	join_room(room)
	# db.execute("INSERT INTO message_table(message,room,username,tima) VALUES(:message,:room,:username,:tima)",
	# 	{"message":message,"room":room,"username":username,"tima":tima})
	emit("display message", {"message": message,"username":username,"time":tima}, room=room, broadcast=True)
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))    	

if __name__=="__main__":
	main()	