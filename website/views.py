from flask import Blueprint, render_template, request
from .models import Product, Sale, StockMovement
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():

    return  render_template("overview.html")

@views.route('/products')
def products():

    products = Product

    return  render_template("products.html", products=products)

@views.route('/create_product')
def create_product():
    product = request.form.get('product')

    return render_template("products.html", product=product)