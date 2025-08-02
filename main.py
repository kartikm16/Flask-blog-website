from flask import Flask,render_template,redirect,url_for,session
import requests
from flask import request
import smtplib
from authlib.integrations.flask_client import OAuth
import secrets
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import os
from dotenv import load_dotenv
import markdown
load_dotenv()

client_secret=os.getenv("client_secret")
client_id=os.getenv("client_id")
sender_email=os.getenv("sender_email")
password=os.getenv("password")
secret_key=os.getenv("secret_key")







app=Flask(__name__)
app.secret_key = "lmst118b"




oauth = OAuth(app)
blogs=requests.get("https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts").json()

google = oauth.register(
    name='google',
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/')
def home():
    user=session.get("user")
    username=""
    if user:
        username=user['given_name']
    blogs=requests.get("https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts").json()
    return render_template("index.html",blogs=blogs,username=username)

@app.route('/<int:id>')
def post(id):
    if session.get('user'):
        return render_template("post.html",post=blogs[id-1],username=session.get('user')['given_name'])
    else :
      return render_template("post.html",post=blogs[id-1],username="")


@app.route('/about')
def about():
    user=session.get("user")
    username=""
    if user:
        username=user['given_name']
    return render_template("about.html",username=username)

@app.route("/contact",methods=["POST","GET"])
def contact():
    user=session.get("user")
    username=""
    if user:
        username=user['given_name']
    if request.method=="POST":
        with smtplib.SMTP_SSL("smtp.gmail.com") as connection:
            connection.login(user=sender_email,password=password)
            connection.sendmail(
                from_addr=sender_email,
                to_addrs="kartik100daysofcode@gmail.com",
                msg=f"Subject:Message from {request.form['name']}\n\n{request.form['message']}\nContact number={request.form['number']}"
            )
        return render_template("contact.html",title="Form submitted succesfully")
    return render_template("contact.html",title='',username=username)

@app.route('/new')
def new():
    user = session.get('user')
    print(user)
    if user:
       return render_template("newpost.html",username=user['given_name'])
    return redirect(url_for("login"))

@app.route('/login')
def login():
    nonce = secrets.token_urlsafe(16)  
    session['nonce'] = nonce           
    redirect_uri = url_for('auth', _external=True)
    print("Redirect URI:", redirect_uri)
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/auth')
def auth():
    token = google.authorize_access_token()
    nonce = session.pop('nonce', None)  # retrieve and remove from session

    # parse ID token with nonce
    userinfo = google.parse_id_token(token, nonce=nonce)

    session['user'] = userinfo
    return redirect('/')

@app.route('/addnewblog',methods=["POST"])
def addnewpost():
    global blogs
    data={
   "id":len(blogs),
   "body":markdown.markdown(request.form["body"]),
   "title":request.form["title"],
   "subtitle":request.form["subtitle"],
   "image_url":request.form["image_url"],
   "posted_by":session.get("user")['given_name'],
   "email":session.get("user")["email"],
   "date":datetime.datetime.now().strftime("%d-%m-%Y")
   }
    requests.post("https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts",json=data)
    blogs=requests.get("https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts").json()
    return redirect(url_for("home"))

@app.route("/myposts")
def myposts():
    user = session.get('user')
    if user:
       useremail=session.get('user')['email']
       userPosts=[post for post in blogs if post["email"]==useremail]

       return render_template("userposts.html",blogs=userPosts,username=user['given_name'])
    return '<a href="/login">Login with Google</a>'
    
@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect("/")
    
@app.route("/edit<int:id>")
def edit(id):
    return render_template("newpost.html",username=session.get("user")["given_name"],blog=blogs[id-1])

@app.route("/updateblog<int:id>",methods=["POST"])
def update(id):
     global blogs
     data={
   "id":len(blogs),
   "body":markdown.markdown(request.form["body"]),
   "title":request.form["title"],
   "subtitle":request.form["subtitle"],
   "image_url":request.form["image_url"],
   "posted_by":session.get("user")['given_name'],
   "email":session.get("user")["email"],
   "date":datetime.datetime.now().strftime("%d-%m-%Y")
   }
     requests.put(f"https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts/{id}",json=data)
     blogs=blogs=requests.get("https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts").json()
     return redirect(url_for('myposts'))
     
@app.route("/delete<int:id>")
def delete(id):
    global blogs
    requests.delete(f"https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts/{id}")
    blogs=requests.get("https://68824e3c66a7eb81224e2dae.mockapi.io/blogposts").json()
    return redirect(url_for("myposts"))





if __name__=="__main__":
    app.run(debug=True)
