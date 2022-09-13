from ast import If
from pickle import NONE
from flask import Flask,g,render_template,request,redirect,flash,session
from sqlalchemy import sql, true
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = "SGNKJGKJSAHFBBHNJSNVKJBSOIBHOGIBGSUC"

DATABASE = 'database.db'

UPLOAD_FOLDER = 'static/'

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


@app.route("/")
def login():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("login.html", results=results)

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
            return redirect('/')

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
                if len(uscreate) > 1:
                    sql = "Select Username FROM User WHERE Username=?"
                    cursor.execute(sql,(uscreate,))
                    result = cursor.fetchone()
                    if result == None:
                        if len(pscreate) > 1:
                            if len(pscreatecheck) > 1:
                                if pscreate == pscreatecheck:
                                    hash = generate_password_hash(pscreate)
                                    sql = "INSERT INTO User (Name,Email,Username,Password) VALUES (?,?,?,?)"
                                    cursor.execute(sql,(nmecreate,emcreate,uscreate,hash))
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
                    return redirect('/signup')
            else:
                return redirect('/signup')
        else:
            return redirect('/signup')
    else:    
        return render_template("signup.html")



@app.route('/admin')
def admin():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("admin.html", results=results)

@app.route('/home')
def home():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    return render_template("home.html", results=results,user=user)

@app.route('/forum')
def forum():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Forum JOIN User ON User.ID = Forum.user_id"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT * FROM reply JOIN Forum ON Forum.ID = reply.post_id"
    cursor.execute(sql)
    reply = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    return render_template("forum.html", results=results, reply=reply, user=user)


@app.route('/donate')
def donate():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    return render_template("donate.html", results=results, user=user)

@app.route('/about')
def about():
    cursor = get_db().cursor()
    sql = "SELECT * FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    return render_template("about.html", results=results, user=user)

@app.route('/profile')
def profile():
    cursor = get_db().cursor()
    sql = "SELECT Profilepic,Username,Name,Email FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    results = cursor.fetchall()

    cursor = get_db().cursor()
    sql = "SELECT Username FROM User WHERE ID=?"
    cursor.execute(sql,(session["user_id"],))
    user = cursor.fetchone()

    return render_template("profile.html", results=results, user=user)

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


@app.route('/addcomment', methods=['GET','POST'])
def addcomment():
    if request.method == "POST":
        comment = request.form["comment"]
        ID = request.form["PostID"]
        db = get_db()
        cursor = db.cursor()
        sql = "INSERT INTO reply (Comment,post_id) VALUES (?,?)"
        result = cursor.execute(sql,(comment,ID))
        db.commit()
        return redirect('/forum')

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





@app.route('/logout', methods=['GET','POST'])
def logout():
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)



