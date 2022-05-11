from flask import render_template, url_for, request, redirect, flash, session
from shop import app, db
from shop.models import Items, User, Review, Address
from shop.forms import RegistrationForm, LoginForm, CheckoutForm, ReviewForm, ShippingForm
from flask_login import login_user, logout_user, current_user
import string
import random
from datetime import date, datetime, timedelta


@app.route("/")
@app.route("/shop", methods=["GET","POST"])
def shop():
  items=Items.query.all()
  if request.method=="POST":
    x = request.form["sort"]
    if x == "price_high":
      session["sort"]=['price',True]
    elif x == "price_low":
      session["sort"]=['price',False]
    elif x == "eco_low":
      session["sort"]=['cbFootprint',False]

    return render_template("shop.html",items=items,sort=session["sort"])
  elif "sort" in session:
    return render_template("shop.html",items=items,sort=session["sort"])
  else:
    session["sort"] = ["id", True]
  return render_template("shop.html",items=items, sort=session["sort"])

@app.route("/leave a review", methods=['GET','POST'])
def leave_review():
  form = ReviewForm()
  if form.validate_on_submit(): 
    review = Review(author_id=current_user.id, item_id=session['item'], content=form.words.data, rating=form.rating.data,)
    db.session.add(review)
    db.session.commit()
    return redirect(url_for('item'))
  return render_template('leave_review_page.html', form=form)

@app.route("/item")
def item():
  reviews = Review.query.filter_by(item_id=session['item']).all()
  item = Items.query.filter_by(id=session['item']).first()
  return render_template('item.html', reviews=reviews, item=item)

@app.route("/current_item", methods=["POST"])
def current_item():
  itemID = request.form["item_id"]
  session['item'] = itemID
  return redirect(url_for('item'))

##logins##
@app.route("/register",methods=['GET','POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    if(form.email.data != None):
      user = User(id=form.username.data, email=form.email.data, password=form.password.data)
    else:
      user = User(id=form.username.data, password=form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Registration successful. Welcome.')
    return redirect(url_for('shop'))
  return render_template('register.html',title='Register', form=form)

@app.route("/login",methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(id=form.username.data).first()
    if user is not None and user.verify_password(form.password.data):
      login_user(user)
      session['user_id'] = user.id
      flash('Login successful!')
      return redirect(url_for('shop'))
    else:
      return redirect(url_for('error_page'))
  return render_template('login.html',title='Login',form=form)

@app.route("/error_page")
def error_page():
  return render_template('error_page.html', title='Error Page')

@app.route("/logout")
def logout():
  logout_user()
  flash('Logout successful. Bye!')
  session.clear()
  return redirect(url_for('shop'))


##cart##
@app.route("/cart",methods=["GET","POST"])
def cart():
  basket = []
  if 'order_num' not in session:
    session['order_num'] = []
  else:
    if session['order_num'] != []:
      session['order_num'] = []
  if 'quantities' not in session:
    session['quantities'] = {}
  quantities = session['quantities']

  if 'cart' not in session:
    session['cart'] = []

  for item in session['cart']:
    item = Items.query.filter_by(id=item).first()
    if item not in basket:
      basket.append(item)

  cost=0
  for item in basket:
    if quantities.get(str(item.id)) == None:
      quantity = 1.00
    else:
      quantity = float(quantities.get(str(item.id)))
    cost += (item.price * quantity)
  cost = round(cost,2)

  session['checkoutTotal'] = cost
  session['checkoutCart'] = session['cart']
  return render_template("cart.html",title="Cart", session=session, basket=basket, quantities=quantities, cost=cost)

@app.route("/add", methods=["POST"])
def add_to_cart():
  itemID = request.form["item_id"]
  if 'cart' not in session:
    session['cart'] = []
  cart_list = session['cart']
  cart_list.append(itemID)
  session['cart'] = cart_list
  return redirect(url_for('shop'))

@app.route("/pop", methods=["POST"])
def pop_item():
  itemID = request.form["item_id"]
  cart_list = session['cart']
  cart_list.pop(cart_list.index(itemID))
  session['cart'] = cart_list
  return redirect(url_for('cart'))

@app.route("/clear", methods=["POST"])
def clear_basket():
  session['cart'] = []
  return redirect(url_for('cart'))

@app.route("/quantity", methods=["POST"])
def change_quantity():
  quantity = request.form["quantity"]
  itemID = request.form["item_id"]
  quantityDict = session['quantities']
  quantityDict[itemID] = quantity
  session['quantities'] = quantityDict
  return redirect(url_for('cart'))

@app.route("/shipping", methods=['GET','POST'])
def shipping():
  form = ShippingForm()
  if form.validate_on_submit():
    if Address.query.filter_by(user_id=session['user_id']).first() != None:
      db.session.delete(Address.query.filter_by(user_id=session['user_id']).first())
      db.session.commit()
    shipping = Address(user_id=session['user_id'], full_name=form.full_name.data, address_1=form.address_1.data, address_2=form.address_2.data,  city_name=form.city_name.data, county_name=form.county_name.data, post_code=form.post_code.data, tel_number=form.tel_number.data)
    db.session.add(shipping)
    db.session.commit()
    flash('Shipping address updated.')
    return redirect(url_for('cart'))
  return render_template('shipping.html', form=form)

##checkout##
@app.route("/checkout",methods=["GET","POST"])
def checkout():
  form = CheckoutForm()
  if form.validate_on_submit():
    session['cart'] = []
    return redirect(url_for('checkout_success'))
  return render_template('checkout.html',title='Checkout',form=form)

@app.route("/checkout_success")
def checkout_success():
  return render_template('checkout_success.html',title='Purchase Complete!')

@app.route("/order_summary")
def order_summary():
  basket=[]
  today = date.today()
  arrival = date.today()+timedelta(days=3)
  order_num = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
  if 'order_num' not in session:
    session['order_num'] = order_num
  elif session['order_num'] == []:
    session['order_num'] = order_num

  if 'user_id' not in session:
    address = None;
    user = None;
  else:
    address = Address.query.filter_by(user_id=session['user_id']).first()
    user = User.query.filter_by(id=session['user_id']).first()
  for item in session['checkoutCart']:
    item = Items.query.filter_by(id=item).first()
    if item not in basket:
      basket.append(item)
  return render_template('order_summary.html', title='Order Summary', address=address, user=user, basket=basket, total=session['checkoutTotal'], quantities=session['quantities'], today=today, arrival=arrival, order_num=session['order_num'])