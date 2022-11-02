from ast import If
import imp
from pickle import NONE
from flask import Flask,g,render_template,request,redirect,flash,session,abort
from sqlalchemy import sql, true
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from PIL import Image

app = Flask(__name__)

app.config['SECRET_KEY'] = "SGNKJGKJSAHFBBHNJSNVKJBSOIBHOGIBGSUC"

DATABASE = 'database.db'

UPLOAD_FOLDER = 'static/'

SESSION = 'session["user_id"]'

# The value that sets the profile picture when signing up
Default = 'Default.jpg'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.errorhandler(400)
def page_not_found(e):
    # Error route for when the user inputs a wrong username or password
    return render_template('incorrect.html'), 400

@app.route("/")
def login():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("signin.html", results=results)

@app.route('/check', methods=['GET','POST'])
def check():
    ## This route checks the text inputed from the HTML login site and sees if the matching 
    # Username + Password Combination has been created and is Correct
    if request.method == "POST":
        User = request.form["usr"]
        Pass = request.form["pwd"]
        cursor = get_db().cursor()
        sql = "SELECT ID,Username,Password FROM User WHERE Username=?;"
        cursor.execute(sql,(User,))
        result = cursor.fetchone()
        if result != None:
            pass_check = check_password_hash(result[2],Pass)
            #Checks if the User is signing in as the PreCreated ADMIN account
            if pass_check == True and User == "ADMIN":
                return redirect('/admin')   
            elif pass_check == True and User == result[1]:
                #Checks the password against the username input in the database and saves the session
                # ID for later use
                session["user_id"]= result[0]  
              
                return redirect('/home')
            else:
                return redirect('/')
        else:
            abort(400)
            

@app.route('/signup', methods=["POST","GET"])
def signup():
    #This route is responsable for Creating and inputing the Users information into the database.
    #It checks to see if the username inputted doesnt match any other username in the database aswell as checks to see if the password and retype password is matching.
    if request.method == "POST":
        nmecreate = request.form["Namecreate"]
        emcreate = request.form["Emailcreate"]
        uscreate = request.form["usrcreate"]
        pscreate = request.form["pwdcreate"]
        pscreatecheck = request.form["pwdcreatecheck"]
        db = get_db()
        cursor = db.cursor()
        if len(nmecreate)  > 1:
            if len(emcreate)  > 1:
                sql = "Select Username FROM User WHERE Username=?"
                cursor.execute(sql,(uscreate,))
                result = cursor.fetchone()
                if result == None:
                    if pscreate == pscreatecheck:
                        hash = generate_password_hash(pscreate)
                        sql = "INSERT INTO User (Name,Email,Username,Password,Profilepic) VALUES (?,?,?,?,?)"
                        cursor.execute(sql,(nmecreate,emcreate,uscreate,hash,Default))
                        db.commit()
                        return redirect ('/')
                    else:
                        return redirect('/signup')
                else:
                    return redirect('/signup')
            else:
                return redirect('/signup')
        else:
            return redirect('/signup')
    else:    
        return render_template("signup.html")


# An admin account used to Monitor and make changes to the website 
@app.route('/admin')
def admin():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall() 
    
    return render_template("admin.html", results=results)


# Yet to be implimented, a function that allows the ADMIN account to delete Forums that are bad
@app.post('/delete')
def delete_item_by_id():
    id = request.form['id']
    cursor = get_db().cursor()
    sql = "DELETE FROM post WHERE id=?"
    cursor.execute(sql, (id, ))
    get_db().commit()
    return redirect('/home')


# The Home page the user is greeted with apon signing into the website
@app.route('/home')
def home():

    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    profile = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()
    
    return render_template("home.html", profile=profile,user=user)


# A Page that allows the user to Post their own discussion Forums and allows them to comment on others
@app.route('/forum')
def forum():
    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    profile = cursor.fetchall()

    # This statement is used to link the user who posted to the forum
    cursor = get_db().cursor()
    sql = "SELECT * FROM Forum JOIN User ON User.ID = Forum.user_id"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM Reply JOIN User ON User.ID = Reply.user_id"
    cursor.execute(sql)
    commentuser = cursor.fetchall()
    # This statement links the individual Comments to the Forum they were commented on
    cursor = get_db().cursor()
    sql = "SELECT * FROM reply JOIN Forum ON Forum.ID = reply.post_id"
    cursor.execute(sql)
    reply = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()
    
    if "user_id" in session == None:
        abort(400)
    else: 
        return render_template("forum.html", results=results, reply=reply, user=user, profile=profile,commentuser=commentuser)

# A page dedicated to act as a portal to a "Kickstarter" site for the websites project
@app.route('/donate')
def donate():

    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    profile = cursor.fetchall()


    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()
    
    if "user_id" in session == None:
        abort(400)
    else: 
        return render_template("donate.html", user=user, profile=profile)

# This page shows off a little description about the project and shows new models of the headsets
@app.route('/about')
def about():

    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    profile = cursor.fetchall()


    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    if "user_id" in session == None:
        abort(400)
    else: 
        return render_template("about.html",user=user, profile=profile)

# The Profile page allows the user to set their own personal profile picture and check the information they set when signing up
# Idealy i would make it so that it allows them to change their data however it isnt implemented as of now
@app.route('/profile')
def profile():

    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    profile = cursor.fetchall()


    # Grabs all of the users information from the database and displays it on the screen
    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    if "user_id" in session == None:
        abort(400)
    else: 
        return render_template("profile.html", results=results, user=user, profile=profile)

# Adds the new forum to the database and updates the page accordingly
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        new_name = request.form["forum_name"]
        print(new_name)
        new_description = request.form["forum_description"]
        print(new_description)
        sql = "INSERT INTO Forum (forumname,forumdescription,user_id) VALUES (?,?,?)"
        cursor.execute(sql,(new_name,new_description,session["user_id"],))
        db.commit()
        return redirect('/forum')

# Used to add the comment to the forum and inputs whatever user commented 
@app.route('/addcomment', methods=['GET','POST'])
def addcomment():
    if request.method == "POST":
        comment = request.form["comment"]
        ID = request.form["PostID"]
        db = get_db()
        userid = session['user_id']
        cursor = db.cursor()
        sql = "INSERT INTO reply (Comment,post_id,user_id) VALUES (?,?,?)"
        cursor.execute(sql, (comment, ID, userid))
        db.commit()
        return redirect('/forum')


# Used to update the Users current profile picture to their new chosen picture
@app.route('/add_item', methods=['GET','POST'])
def add_item():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(UPLOAD_FOLDER+filename)
        sql = "UPDATE User SET Profilepic = ? WHERE ID=?;"
        picture = cursor.execute(sql,(filename,session["user_id"]))
        db.commit()
        return redirect('/profile')


# The logout button allowing the  user to return to the login/signup area
@app.route('/logout', methods=['GET','POST'])
def logout():
    session.clear(  )
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)



