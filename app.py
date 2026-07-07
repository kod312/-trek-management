 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Trek, Booking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trek.db'
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables created!")
    app.run(debug=True)