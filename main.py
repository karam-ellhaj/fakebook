
from flask import Flask, session,request,flash
import os
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import escape, redirect,secure_filename
import re
UPLOAD_PTAH = "./static/uploads"
app = Flask(__name__)
app.config["SECRET_KEY"] = "21:41_4_oct_vscode"
 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db" # change it to actual database uri
db = SQLAlchemy(app)
#the folder were all the photos upload to
app.config["UPLOAD_FOLDER"] = UPLOAD_PTAH
#the allowed file types (potos only allowed)
allowed_ex = {"png","jpeg","jpg","svg","gif","webp"}
#email regex for validating emails 
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


#the users table
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True) # a unique id 
    name = db.Column(db.String(25))
    email = db.Column(db.String(70))
    password = db.Column(db.String(30))
    messages = db.relationship("Posts",backref='author')#the posts written by the user

class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    post = db.Column(db.Text)
    image = db.Column(db.String(100))
    author_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer)


#for creating the database file (not recommended on deployment)
# db.create_all() 
# db.session.commit()

#function  to validate the files
def allowed(filename):
    return "." in filename and filename.rsplit('.',1)[1].lower() in allowed_ex

@app.route("/")
def index():
    
    if "user_id" in session:
        current_user = Users.query.filter_by(id=session["user_id"]).first()
        posts = Posts.query.filter_by(post_id=None).all()
        return render_template("index.html",posts=posts,current_user=current_user)
    else:
        return redirect("/login")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if "user_id" in session:return redirect("/")
    if request.method == "POST":  
        user_object=request.form
        name = user_object["name"]
        email = user_object["email"]
        password = user_object["password"]
        confirm_password = user_object["confirm-password"]
        usr = Users.query.filter_by(email=email).first()
        if usr:
            return "user already exists"
        if re.fullmatch(email_regex, email):
            if password == confirm_password and password.__len__() > 8: 
                user = Users(name=name,email=email,password=password)
                db.session.add(user) 
                db.session.commit()
                print(user)
            else:return"password is short or not equel to confirm password "
        else:return "email is not valid"
    return render_template("signup.html")
   

@app.route("/send_post",methods=["POST"])
def send():
    current_user = Users.query.filter_by(id=session["user_id"]).first()

    post = request.form["post"]
    img = request.files["img"]

    if allowed(secure_filename(img.filename)):
        img.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(img.filename)))
        pst = Posts(post=post,author=current_user
        ,image=os.path.join(app.config["UPLOAD_FOLDER"],
        secure_filename(img.filename)),post_id=None)
        print(post)
        db.session.add(pst)
        db.session.commit()
        return redirect("/") 

    pst = Posts(post=post,author=current_user)
    db.session.add(pst)
    db.session.commit()
    return redirect("/")
    

@app.route("/login",methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    if request.method == "POST" :
        user = request.form
        email = user["email"]
        password = user["password"]
        usr = Users.query.filter_by(email=email).first()
        if usr:
            if usr.password == password:
                session["user_id"] = usr.id
                return redirect("/")
            else:return "password is not correct"
        else:return "email does not exist"
    return render_template("login.html")
@app.route("/delete_post")
def delete_post():
    current_user = Users.query.filter_by(id=session["user_id"]).first()
    post = request.args["post"]
    p = Posts.query.filter_by(id=post)
    if p.first().author.id == current_user.id:
        p.delete()
        db.session.commit()
    else:make_response("you must be the author to delete the Post",403)
    if "id" in request.args:
        
        return redirect("/comments?post_id="+request.args["id"])  
    return redirect("/")

@app.route("/comments")
def comments():
    if "user_id" in session:
        post = request.args["post_id"]
        comments = Posts.query.filter_by(post_id=post).all()
        return render_template("comments.html",comments=comments,post_id=post)

@app.route("/send_comment",methods=["POST"])
def send_comment():
    current_user = Users.query.filter_by(id=session["user_id"]).first()
    id = request.form["post_id"]
    post = request.form["post"]
    if "img" in request.files:
        img = request.files["img"]
    else:
        img = None

    if allowed(secure_filename(img.filename)):
        img.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(img.filename)))
        pst = Posts(post=post,author=current_user
        ,image=os.path.join(app.config["UPLOAD_FOLDER"],
        secure_filename(img.filename)),post_id=id)
        print(post)
        db.session.add(pst)
        db.session.commit()
        return redirect("/comments?post_id="+id) 

    pst = Posts(post=post,author=current_user,post_id=id)
    print(pst.post)
    db.session.add(pst)
    db.session.commit()
    return redirect("/comments?post_id="+id)

@app.route("/profile")
def  pro():
    if "user_id" in session:
        user = Users.query.filter_by(id=session["user_id"]).first()
        print(user)
        return render_template("profile.html",user=user.name,email=user.email)

@app.route("/logout")
def logout():
    if "user_id" in session:
        session.popitem() 
        return redirect("/login")


if __name__=="__main__":
    app.run(debug=True)#,host="192.168.43.119")