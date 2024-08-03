from flask import Blueprint, render_template, request
from models import Product, Sale, StockMovement
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():

    products = Product.all()

    return  render_template("home.html", products=products)

@views.route('/create_product')
def create_product():
    product = request.form.get('product')

    return render_template("products.html", product=product)