import email_validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField,TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Regexp, Email, Length, NumberRange, Optional
from shop.models import User
from wtforms.validators import ValidationError

class RegistrationForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired(), Length(min=5, max=20)])
  email = StringField('Email', validators=[Optional(), Email()])
  password = PasswordField('Password',validators=[DataRequired(), Length(min=5, max=20), EqualTo('confirm_password', message='Passwords do not match, please try again')])
  confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
  submit = SubmitField('Sign up')

  def validate_username(self, username):
    user = User.query.filter_by(id=username.data).first()
    if user is not None:
      raise ValidationError('Username already exist. Please choose a different one.')


class LoginForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired(), Length(min=5, max=20)])
  password = PasswordField('Password',validators=[DataRequired(), Length(min=5, max=20)])
  submit = SubmitField('Login')

class CheckoutForm(FlaskForm):
  name = StringField("Name",validators=[DataRequired()])
  card_no = StringField("Card Number",validators=[DataRequired(),Regexp('^[0-9]*$',message="Card number must only contain numbers"),Length(min=16,max=16)])
  submit = SubmitField('Checkout')

class ReviewForm(FlaskForm):
  rating = IntegerField("Rating", validators=[DataRequired(), NumberRange(min=1, max=5, message="Needs to be between 1 and 5")], default=1, )
  words = TextAreaField("Leave a Review",validators=[DataRequired()], description='Write a review')
  submit = SubmitField('Submit')

class ShippingForm(FlaskForm):
  full_name = StringField("Full Name", validators=[DataRequired()])
  address_1 = StringField("Address", validators=[DataRequired()])
  address_2 = StringField("", validators=[Optional()])
  city_name = StringField("City", validators=[DataRequired()])
  county_name = StringField("County", validators=[DataRequired()])
  post_code = StringField("Post Code", validators=[DataRequired()])
  tel_number = StringField("Telephone", validators=[DataRequired(), Regexp('^[0-9]*$',message="Tel is numbers only"), Length(min=11, max=12)])
  submit = SubmitField('Submit')