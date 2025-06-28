from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(200))

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(200))
    description = db.Column(db.String(300))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy=True))


@app.route('/')
def home():
    categories = Category.query.all()
    return render_template("index.html", categories=categories)

@app.route('/category/<int:category_id>')
def category_view(category_id):
    category = Category.query.get_or_404(category_id)
    products = Products.query.filter_by(category_id=category.id).all()
    return render_template("category.html", category=category, products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Products.query.get_or_404(product_id)

    cart = session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    session['cart'] = cart
    return redirect(url_for('view_cart'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/update_cart/<int:product_id>/<action>')
def update_cart(product_id, action):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        if action == 'increase':
            cart[str(product_id)] += 1
        elif action == 'decrease':
            cart[str(product_id)] = max(1, cart[str(product_id)] - 1)
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))


@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    products = []
    total = 0

    for pid, qty in cart.items():
        product = Products.query.get(int(pid))
        subtotal = product.price * qty
        total += subtotal
        products.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal
        })

    gst = int(total * 0.18)
    final_total = total + gst

    return render_template("cart.html", products=products, total=total, gst=gst, final_total=final_total)





if __name__ == '__main__':
    app.run(debug=True)