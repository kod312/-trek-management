 
from flask import Flask, render_template,request,redirect,url_for,flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Trek, Booking
from flask_login import LoginManager, login_user,logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek.db'
app.config['SECRET_KEY'] = 'superdupersecretultrakey123'
db.init_app(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html')
	elif request.method == 'POST':
		username=request.form.get('username')
		email=request.form.get('email')
		password=request.form.get('password')
		hashedpassword=generate_password_hash(password)
		new_user= User(username=username, email=email, password=hashedpassword, role='trekker')
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		username=request.form.get('username')
		password=request.form.get('password')
		user= User.query.filter_by(username=username).first()
		if user and check_password_hash(user.password,password)==True:
			login_user(user)
			if user.role== 'trekker':
				return redirect(url_for('trekker'))
			elif user.role== 'staff':
				return redirect(url_for('staff'))
			else:
				return redirect(url_for('admin'))
		else:
			return redirect(url_for('login'))
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))
@app.route('/admin')
def admin():
    return "Admin - soon"

@app.route('/staff')
def staff():
    return "Staff - soon"

@app.route('/trekker')
def trekker():
    return "Trekker - soon"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables created!")
    app.run(debug=True)