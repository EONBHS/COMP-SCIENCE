from pickle import NONE
from flask import Flask,g,render_template,request,redirect
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3

app = Flask(__name__)



DATABASE = 'database.db'

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
def home():
    cursor = get_db().cursor()
    sql = "SELECT * FROM UserID"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("login.html", results=results)

@app.route('/check', methods=['GET','POST'])
def check():
    if request.method == "POST":
        User = request.form["usr"]
        Pass = request.form["pwd"]
        cursor = get_db().cursor()
        sql = "SELECT Username,Password FROM UserID WHERE Username=?;"
        cursor.execute(sql,(User,))
        result = cursor.fetchone()
        if result != None:
            pass_check = check_password_hash(result[1],Pass)
            if pass_check == True and User == "ADMIN":
                return redirect('/admin')
        else:
            return redirect('/')

@app.route('/signup', methods=["POST","GET"])
def signup():
    if request.method == "POST":
        emcreate = request.form["Emailcreate"]
        uscreate = request.form["usrcreate"]
        pscreate = request.form["pwdcreate"]
        pscreatecheck = request.form["pwdcreatecheck"]
        print(emcreate)
        print(uscreate)
        print(pscreate)
        print(pscreatecheck)
    else:    
        return render_template("signup.html")



@app.route('/admin')
def login():
    return 'admin'


if __name__ == "__main__":
    app.run(debug=True)
