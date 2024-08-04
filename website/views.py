from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from .models import Product
from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("overview.html")


@views.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        name = request.form.get("name")
        sku = request.form.get("sku")
        category = request.form.get("category")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        supplier = request.form.get("supplier")
        description = request.form.get("description")

        errors = []
        if not name:
            errors.append("Name is required.")
        if not sku:
            errors.append("SKU is required.")
        elif Product.query.filter_by(sku=sku).first():
            errors.append("SKU already exists.")
        if not price or not price.replace(".", "", 1).isdigit():
            errors.append("Price is required and must be a number.")
        if not quantity or not quantity.isdigit():
            errors.append("Quantity is required and must be an integer.")

        if errors:
            flash(" ".join(errors), "danger")
        else:
            new_product = Product(
                name=name,
                sku=sku,
                category=category,
                price=float(price),
                quantity=int(quantity),
                supplier=supplier,
                description=description,
            )
            db.session.add(new_product)
            db.session.commit()
            flash("Product has been successfully added!", "success")
            return redirect(url_for("views.products"))

    products = Product.query.all()
    return render_template("products.html", products=products)


@views.route("/delete_product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)

    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Product not found."}), 404


@views.route("/edit_product/<int:product_id>", methods=["POST"])
def edit_product(product_id):
    product = Product.query.get(product_id)

    if product:
        product.name = request.form.get("name")
        product.sku = request.form.get("sku")
        product.category = request.form.get("category")
        product.price = request.form.get("price")
        product.quantity = request.form.get("quantity")
        product.supplier = request.form.get("supplier")
        product.description = request.form.get("description")

        db.session.commit()
        flash("Product updated successfully!", "success")
    else:
        flash("Product not found.", "danger")

    return redirect(url_for("views.products"))

@views.route('/get_product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'name': product.name,
        'sku': product.sku,
        'category': product.category,
        'price': product.price,
        'quantity': product.quantity,
        'supplier': product.supplier,
        'description': product.description
    })
