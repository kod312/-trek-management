 
from flask import Flask, render_template,request,redirect,url_for,flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Trek, Booking
from flask_login import LoginManager, login_user,logout_user, login_required, current_user
from datetime import date

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
@login_required
def admin():
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	trekker_count=User.query.filter_by(role='trekker').count()
	staff_count=User.query.filter_by(role='staff').count()
	no_of_treks=Trek.query.count()
	no_of_bookings=Booking.query.count()
	return render_template('admin_dashboard.html',
	trekker_count=trekker_count,staff_count=staff_count,no_of_treks=no_of_treks,
	no_of_bookings=no_of_bookings)

@app.route('/admin/treks')
@login_required
def admin_treks():
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	treks=Trek.query.all()
	return render_template('admin_treks.html',
	treks=treks)

@app.route('/staff')
@login_required
def staff():
	if current_user.role != 'staff':
		return redirect(url_for('trekker'))
	if current_user.status != 'approved':
		return render_template('pending_approval.html')
	treks= Trek.query.filter_by(assigned_staff_id=current_user.id).all()
	return render_template('staff_dashboard.html', treks=treks)

@app.route('/staff/register', methods=['GET', 'POST'] )
def staff_register():
	if request.method == 'GET':
        	return render_template('staff_register.html')
	elif request.method == 'POST':
		username= request.form.get('username')
		email= request.form.get('email')
		password= request.form.get('password')
		hashed= generate_password_hash(password)
		new_staff= User(username=username,email=email,password=hashed,role='staff', status='pending')
		db.session.add(new_staff)
		db.session.commit()
	return redirect(url_for('login'))

@app.route('/staff/trek/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def staff_edit_trek(id):
	if current_user.role != 'staff':
        	return redirect(url_for('trekker'))
	trek=Trek.query.get(id)
	if trek.assigned_staff_id != current_user.id:
		return redirect(url_for('staff'))
	if request.method == 'GET':
		return render_template('staff_edit_trek.html', trek=trek)
	elif request.method == 'POST':
		trek.available_slots= request.form.get('available_slots')		
		trek.status= request.form.get('status')
		db.session.commit()
		return redirect(url_for('staff'))

@app.route('/staff/trek/participants/<int:trek_id>')
@login_required
def trek_participants(trek_id):
	if current_user.role != 'staff':
		return redirect(url_for('trekker'))
	bookings = Booking.query.filter_by(trek_id=trek_id).all()
	return render_template('participants.html', bookings=bookings)

@app.route('/trekker')
@login_required
def trekker():
	if current_user.role != 'trekker':
		return redirect(url_for('login'))
	treks= Trek.query.filter_by(status='Open').all()
	return render_template('trekker_dashboard.html', treks=treks)

@app.route('/book/<int:trek_id>')
@login_required
def book_trek(trek_id):
	if current_user.role != 'trekker':
		return redirect(url_for('login'))
	trek = Trek.query.get(trek_id)
	if trek.status == 'Open' and trek.available_slots > 0:
		trek.available_slots -= 1
		booking = Booking(
		user_id=current_user.id, 
		trek_id=trek_id, 
		booking_date=str(date.today()), 
		status='Booked')
		db.session.add(booking)
		db.session.commit()
	return redirect(url_for('trekker'))

@app.route('/trekker/bookings')
@login_required
def booking_history():
	if current_user.role != 'trekker':
		return redirect(url_for('login'))
	bookings = Booking.query.filter_by(user_id=current_user.id).all()
	return render_template('booking_history.html', bookings=bookings)

@app.route('/trekker/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	if request.method == 'GET':
        	return render_template('edit_profile.html', user=current_user)
	elif request.method == 'POST':
		current_user.name = request.form.get('name')
		current_user.contact = request.form.get('contact')
		db.session.commit()
		return redirect(url_for('trekker'))

@app.route('/trekker/search')
@login_required
def search_treks():
	difficulty = request.args.get('difficulty')
	location = request.args.get('location')
	query = Trek.query.filter_by(status='Open')
	if difficulty:
		query = query.filter_by(difficulty=difficulty)
	if location:
		query = query.filter(Trek.location.contains(location))
	treks = query.all()
	return render_template('search_treks.html', treks=treks)


@app.route('/admin/trek/create',methods=['GET', 'POST'])
@login_required
def create_trek():
	if current_user.role !='admin':
		return redirect(url_for('trekker'))
	if request.method == 'GET':
		return render_template('create_trek.html')
	elif request.method == 'POST':
		name=request.form.get('name').strip()
		location=request.form.get('location').strip()
		difficulty=request.form.get('difficulty').strip()
		duration=request.form.get('duration').strip()		
		available_slots=request.form.get('available_slots').strip()
		status=request.form.get('status').strip()
		start_date=request.form.get('start_date').strip()
		end_date=request.form.get('end_date').strip()
		new_trek= Trek(name=name,location=location,difficulty=difficulty,duration=duration,available_slots=available_slots,status=status,start_date=start_date,end_date=end_date)
		db.session.add(new_trek)
		db.session.commit()
		return redirect(url_for('admin_treks'))

@app.route('/admin/trek/edit/<int:id>',methods=['GET', 'POST'])
@login_required
def edit_trek(id):
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	trek=Trek.query.get(id)
	if request.method == 'GET':
		return render_template('edit_trek.html', trek=trek)
	elif request.method == 'POST':
		trek.name =request.form.get('name')
		trek.location =request.form.get('location')
		trek.difficulty =request.form.get('difficulty')
		trek.duration =request.form.get('duration')
		trek.available_slots =request.form.get('available_slots')
		trek.status =request.form.get('status')
		trek.start_date =request.form.get('start_date')
		trek.end_date =request.form.get('end_date')
		db.session.commit()
		return redirect(url_for('admin_treks'))

@app.route('/admin/search')
@login_required
def admin_search():
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	query = request.args.get('q', '')
	users = User.query.filter(User.username.contains(query)).all()
	treks = Trek.query.filter(Trek.name.contains(query)).all()
	return render_template('admin_search.html', users=users, treks=treks, query=query)

@app.route('/admin/trek/delete/<int:id>')
@login_required
def delete_trek(id):
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	trek=Trek.query.get(id)
	db.session.delete(trek)
	db.session.commit()
	return redirect(url_for('admin_treks'))

@app.route('/admin/users')
@login_required
def admin_users():
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	users=User.query.filter_by(role='trekker').all()
	return render_template('admin_users.html',
	users=users)

@app.route('/admin/user/blacklist/<int:id>')
@login_required
def blacklist(id):
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	user=User.query.get(id)
	user.is_blacklisted=True
	db.session.commit()
	return redirect( url_for('admin_users'))

@app.route('/admin/staff')
@login_required
def admin_staff():
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	staff=User.query.filter_by(role='staff').all()
	return render_template('admin_staff.html',
	staff=staff)

@app.route('/admin/staff/approve/<int:id>')
@login_required
def approve_staff(id):
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	user=User.query.get(id)
	user.status= 'approved'
	db.session.commit()
	return redirect (url_for('admin_staff'))

@app.route('/admin/trek/assign/<int:trek_id>',methods=['GET', 'POST'])
@login_required
def assign_staff(trek_id):
	if current_user.role != 'admin':
		return redirect(url_for('trekker'))
	trek= Trek.query.get(trek_id)
	staff= User.query.filter_by(role='staff', status='approved').all()
	if request.method == 'GET':
		return render_template('assign_staff.html', trek=trek, staff=staff)
	elif request.method == 'POST':
		staff_id= request.form.get('staff_id')
		trek.assigned_staff_id= staff_id
		db.session.commit()
		return redirect(url_for('admin_treks'))
if __name__ == '__main__':
	with app.app_context():
		db.create_all()
		admin=User.query.filter_by(role='admin').first()
		if not admin:
			admin_user=User(
				username='admin',
				email='admin@gmail.com', 
				password= generate_password_hash('a123'), 
				role='admin'
			)
			db.session.add(admin_user)
			db.session.commit()
			print("Admin created!")
		print("Tables created!")
	app.run(debug=True)