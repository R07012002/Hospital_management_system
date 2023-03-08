from flask import Flask, render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail






db = SQLAlchemy()

    
app = Flask(__name__,template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/hms'
db.init_app(app)
app.secret_key = 'rutuja'

login_manager=LoginManager(app)
login_manager.login_view="login"

# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='578',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-password']
# )
# mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=True)
    username=db.Column(db.String(100))
    password=db.Column(db.String(1000))


class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))
    


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/details",methods=['POST','GET'])
@login_required
def details():
    # posts=Trigr.query.filter_by(tid=tid).first()
    posts=db.engine.execute("SELECT * FROM trigr")
    return render_template('trigers.html')
      
   


@app.route("/index")
def index():
     if not User.is_authenticated:
            return render_template('login.html')
     else:
            return render_template('index.html')
# return render_template('index.html')
   
    
    
@app.route('/doctors',methods=['POST','GET'])
@login_required
def doctors():

    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')
        query=db.engine.execute(f"INSERT INTO `doctors` (`email`,`doctorname`,`dept`) VALUES ('{email}','{doctorname}','{dept}')")
        flash("Information is Stored","primary")

    return render_template('doctor.html')

@app.route("/patients",methods=['GET', 'POST'])
@login_required 
def patients():
    doct=db.engine.execute("SELECT * FROM doctors")
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        
        query=db.engine.execute(f"INSERT INTO `patients` (`Email`,`name`,	`gender`,`slot`,`disease`,`time`,`date`,`dept`,`number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{time}','{date}','{dept}','{number}')")
      
        
        flash("Booking Confirmed","info")
    return render_template('patients.html',doct=doct)
    
    
   
    
    
         

@app.route("/bookingdetails")
@login_required
def bookingdetais():
    em=current_user.email
    query=db.engine.execute(f"SELECT * FROM patients WHERE email='{em}'")
    return render_template('bookingdetails.html',query=query)

@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        db.engine.execute(f"UPDATE `patients` SET `email` = '{email}', `name` = '{name}', `gender` = '{gender}', `slot` = '{slot}', `disease` = '{disease}', `time` = '{time}', `date` = '{date}', `dept` = '{dept}', `number` = '{number}' WHERE `patients`.`pid` = {pid}")
        flash("Slot is Updated","success")
        return redirect('/bookingdetails')
    
    return render_template('edit.html',posts=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`pid`={pid}")
    flash("Slot Deleted Successful","danger")
    return redirect('/bookingdetails')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
             flash("Email Exits","warning")
             return render_template('/signup.html')
        encpassword=generate_password_hash(password)               
       
        new_user=User(username=username, email=email,password=encpassword)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Success")
        return render_template('login.html')
             
    
    return render_template('/signup.html')



@app.route("/login", methods=['GET', 'POST'])
def login():
     if request.method == 'POST': 
         email = request.form.get('email')
         password = request.form.get('password')
         user=User.query.filter_by(email=email).first()

         if user and check_password_hash(user.password,password):
                login_user(user)
                flash("Login Success","primary")
                return redirect(url_for('index'))
         else:
                flash("Invalid Credentials","danger")
                return render_template('login.html')
     return render_template('login.html')
     
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul")
    return redirect(url_for('login'))

        
@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    if request.method=="POST":
        query=request.form.get('search')
        dept=Doctors.query.filter_by(dept=query).first()
        name=Doctors.query.filter_by(doctorname=query).first()
            
        if name:

            flash("Doctor is Available","info")
        else:

            flash("Doctor is Not Available","danger")
    return render_template('index.html')

    
app.run(debug=True)
# if __name__ == '_main_':
    
#


