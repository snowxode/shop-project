from shop import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(str(user_id))

class Items(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  content = db.Column(db.Text, nullable=False)
  price = db.Column(db.Float, nullable=False)
  cbFootprint = db.Column(db.Integer, nullable=False )
  image_file = db.Column(db.String(40), nullable=False, default='default.jpg')

  def __repr__(self):
    return f"Item(' {self.title}', '{self.content}', '{self.price}',' {self.cbFootprint}')"

class User(UserMixin,db.Model):
  id = db.Column(db.String(15), unique=True, nullable=False, primary_key=True)
  email = db.Column(db.String(40), nullable=True)
  hashed_password=db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return (self.id)
    
  @property
  def password(self):
    raise AttributeError('Password is not readable.')

  @password.setter
  def password(self,password):
    self.hashed_password=generate_password_hash(password)

  def verify_password(self,password):
    return check_password_hash(self.hashed_password,password)

class Review(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
  date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  content = db.Column(db.Text, nullable=False)
  rating = db.Column(db.Integer, nullable=False)
  
  user = db.relationship('User', backref='user', lazy=True)
  item = db.relationship('Items', backref='items', lazy=True)

  def __repr__(self):
    return f"Item(' {self.author_id}', '{self.item_id}', '{self.content}', '{self.rating}')"

class Address(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  full_name = db.Column(db.Text, nullable=False)
  address_1 = db.Column(db.Text, nullable=False)
  address_2 = db.Column(db.Text, nullable=True)
  city_name = db.Column(db.Text, nullable=False)
  county_name = db.Column(db.Text, nullable=False)
  post_code = db.Column(db.Text, nullable=False)
  tel_number = db.Column(db.Text, nullable=False)

  def __repr__(self):
    return f"Item(' {self.user_id}', '{self.tel_number}')"
