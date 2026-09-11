from flask import Flask,request,redirect,render_template,session,jsonify
import mysql.connector
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

app=Flask(__name__)
app.secret_key=os.environ.get("secret_key")
app.permanent_session_lifetime=timedelta(seconds=30)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="EmployeeManagement"
)

@app.route('/')
def home():
    return render_template("login.html")


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        role=request.form["role"]
        hashed_password=generate_password_hash(password)

        cursor=conn.cursor()
        cursor.execute("insert into users(username,password,role)values(%s,%s,%s)",
                       (username,hashed_password,role))
        conn.commit()
        cursor.close()
        return f"""registration successfil.. <a href="/login">Login</a> """
    return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        cursor=conn.cursor()
        cursor.execute("select * from users where username=%s",
                       (username,))
        user=cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user[2],password):
            session.permanent=True
            session["login"]=True
            session["username"]=username
            return redirect('/dashboard')
        return f"Invalid username or password..."
    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if session.get('login'):
        username=session["username"]
        return render_template("dashboard.html",username=username)
    return redirect('/')

@app.route('/add_employee',methods=['GET','POST'])
def add_employee():
    if session.get('login'):
        
        if request.method=='POST':
            eid=request.form['eid']
            ename=request.form['ename']
            edept=request.form['edept']
            esalary=request.form['esalary']
            ephone=request.form['ephone']

            cursor=conn.cursor()
            cursor.execute("insert into employee(eid,ename,edept,esalary,ephone)values(%s,%s,%s,%s,%s)",
                        (eid,ename,edept,esalary,ephone))
            conn.commit()
            cursor.close()
            return redirect('/view_employee')
        return render_template('add_employee.html')
    return redirect('/')
        
@app.route('/view_employee')
def view_employee():
    if session.get('login'):
        search=request.args.get('search','')
        cursor=conn.cursor()
        if search:
            cursor.execute("""select * from employee where ename like %s 
            or eid like %s
            or edept like %s""",
            ('%'+search+'%','%'+search+'%','%'+search+'%'))
        else:
            cursor.execute('select * from employee')
        employees=cursor.fetchall()
        cursor.close()
        return render_template('view_employee.html',employees=employees)
    return redirect('/')

@app.route('/edit_employee/<int:eid>',methods=['POST','GET'])
def edit_employee(eid):
    if session.get("login"):
        if request.method=="POST":
            ename=request.form["ename"]
            edept=request.form["edept"]
            esalary=request.form["esalary"]
            ephone=request.form["ephone"]

            cursor=conn.cursor()
            cursor.execute("update employee set ename=%s,edept=%s,esalary=%s,ephone=%s where eid=%s",
                           (ename,edept,esalary,ephone,eid))
            conn.commit()
            cursor.close()
            return redirect('/view_employee')
        cursor = conn.cursor()
        cursor.execute("select * from employee where eid=%s",(eid,))
        employee=cursor.fetchone()
        cursor.close()
        return render_template('edit_employee.html',employee=employee)
    return redirect('/')

@app.route('/delete_employee/<int:eid>')
def delete_employee(eid):
    if session.get('login'):
        cursor=conn.cursor()
        cursor.execute("delete from employee where eid=%s",(eid,))
        conn.commit()
        cursor.close()
        return redirect('/view_employee')
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


app.run(debug=True)
















