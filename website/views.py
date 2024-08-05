import csv
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from .models import Product, Category
from werkzeug.utils import secure_filename
from . import db

views = Blueprint("views", __name__)

@views.route("/")
def home():
    return render_template("overview.html")

@views.route("/products", methods=["GET", "POST"])
def products():
    selected_category = request.args.get("category", "")

    if request.method == "POST":
        # Process form data for adding or editing products
        if 'edit_product_id' in request.form:
            product_id = int(request.form.get("edit_product_id"))
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

    products = Product.query.filter(Product.category.like(f"%{selected_category}%")).all()
    categories = Category.query.all()
    return render_template("products.html", products=products, categories=categories, selected_category=selected_category)

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

@views.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        if category_name:
            # Add new category
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for('views.manage_categories'))

    categories = Category.query.all()
    return render_template('manage_categories.html', categories=categories)

@views.route('/delete_category', methods=['POST'])
def delete_category():
    category_id = request.form.get('category_id')
    if category_id:
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
    return redirect(url_for('views.manage_categories'))

@views.route("/search_products", methods=["GET"])
def search_products():
    query = request.args.get("query", "")
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': product.price,
        'description': product.description
    } for product in products])

@views.route('/import_csv', methods=['POST'])
def import_csv():
    if 'csv_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('views.products'))

    file = request.files['csv_file']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('views.products'))

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = f"uploads/{filename}"  # Adjust this path as needed
        file.save(file_path)

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get('name')
                sku = row.get('sku')
                category = row.get('category')
                price = row.get('price')
                quantity = row.get('quantity')
                supplier = row.get('supplier')
                description = row.get('description')

                # Check for existing SKU
                existing_product = Product.query.filter_by(sku=sku).first()
                if existing_product:
                    # Update existing product
                    existing_product.name = name
                    existing_product.category = category
                    existing_product.price = float(price)
                    existing_product.quantity = int(quantity)
                    existing_product.supplier = supplier
                    existing_product.description = description
                else:
                    # Create new product
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
            flash('Products imported successfully!', 'success')

    else:
        flash('Invalid file format. Please upload a CSV file.', 'danger')

    return redirect(url_for('views.products'))