import csv
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from .models import Product, Category, StockMovement
from werkzeug.utils import secure_filename
from . import db

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("overview.html")


@views.route("/products", methods=["GET"])
def products():
    selected_category = request.args.get("category", "")
    products = Product.query.filter(
        Product.category.like(f"%{selected_category}%")
    ).all()
    
    product_stock = {}
    current_quantities = {}
    for product in products:
        stock_movements = StockMovement.query.filter_by(product_id=product.id).all()
        
        # Calculate the current quantity for each product
        current_quantity = 0

        for movement in stock_movements:
            if movement.movement_type == 'addition':
                current_quantity += movement.change_quantity
            elif movement.movement_type == 'removal':
                current_quantity -= movement.change_quantity

        current_quantities[product.id] = current_quantity
    
    products = products[::-1]
    categories = Category.query.all()

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        selected_category=selected_category,
        current_quantities=current_quantities
    )


@views.route("/edit_product", methods=["GET", "POST"])
@views.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id=None):
    categories = Category.query.all()  # Fetch all categories for the dropdown

    if product_id:
        # Editing an existing product
        product = Product.query.get_or_404(product_id)
        if request.method == "POST":
            product.name = request.form.get("name")
            product.sku = request.form.get("sku")
            product.category = request.form.get("category")
            product.price = float(request.form.get("price"))
            sale_price = request.form.get("sale_price")
            print(f"Received sale_price: '{sale_price}'")
            product.sale_price = float(sale_price) if sale_price else None
            print(f"Processed sale_price: {product.sale_price}")
            product.supplier = request.form.get("supplier")
            product.description = request.form.get("description")
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("views.products"))
        return render_template(
            "edit_product.html", product=product, categories=categories
        )

    else:
        # Adding a new product
        if request.method == "POST":
            name = request.form.get("name")
            sku = request.form.get("sku")
            category = request.form.get("category")
            price = request.form.get("price")
            sale_price = request.form.get("sale_price")
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
            if sale_price and not sale_price.replace(".", "", 1).isdigit():
                errors.append("Sale price must be a number.")

            if errors:
                flash(" ".join(errors), "danger")
            else:
                sale_price = float(sale_price) if sale_price and sale_price.strip() else None

                print(f"Price: {price}")
                print(f"Sale Price: {sale_price}")

                new_product = Product(
                    name=name,
                    sku=sku,
                    category=category,
                    price=float(price),
                    sale_price=sale_price,
                    supplier=supplier,
                    description=description,
                )
                db.session.add(new_product)
                db.session.commit()
                flash("Product has been successfully added!", "success")
                return redirect(url_for("views.products"))

        return render_template("edit_product.html", product=None, categories=categories)


@views.route("/delete_product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)

    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Product not found."}), 404


@views.route("/get_product/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(
        {
            "name": product.name,
            "sku": product.sku,
            "category": product.category,
            "price": product.price,
            "sale_price": product.sale_price,
            "supplier": product.supplier,
            "description": product.description,
        }
    )


@views.route("/categories", methods=["GET", "POST"])
def manage_categories():
    if request.method == "POST":
        category_name = request.form.get("category_name")
        if category_name:
            # Add new category
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for("views.manage_categories"))

    categories = Category.query.all()
    return render_template("manage_categories.html", categories=categories)


@views.route("/manage_stock", methods=["GET", "POST"])
def manage_stock():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        change_quantity = int(request.form.get("change_quantity"))
        movement_type = request.form.get("movement_type")
        description = request.form.get("description")

        if movement_type not in ['addition', 'removal']:
            flash("Invalid movement type!", "danger")
            return redirect(url_for("views.manage_stock"))

        stock_movement = StockMovement(
            product_id=product_id,
            change_quantity=change_quantity,
            movement_type=movement_type,
            description=description,
        )
        db.session.add(stock_movement)
        db.session.commit()
        flash("Stock updated successfully!", "success")
        return redirect(url_for("views.manage_stock"))

    products = Product.query.all()
    products = products[::-1]
    
    # Prepare product details including stock movements and current quantity
    product_stock_details = {}
    for product in products:
        stock_movements = StockMovement.query.filter_by(product_id=product.id).all()
        current_quantity = 0

        for movement in stock_movements:
            if movement.movement_type == 'addition':
                current_quantity += movement.change_quantity
            elif movement.movement_type == 'removal':
                current_quantity -= movement.change_quantity
        
        # Convert StockMovement objects to dictionaries
        stock_movement_list = [{
            "change_quantity": movement.change_quantity,
            "movement_type": movement.movement_type,
            "movement_date": movement.movement_date.strftime('%Y-%m-%d %H:%M:%S'),
            "description": movement.description
        } for movement in stock_movements]
        
        product_stock_details[product.id] = {
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "sale_price": product.sale_price,
            "description": product.description,
            "current_quantity": current_quantity,
            "stock_movements": stock_movement_list
        }
    
    return render_template(
        "manage_stock.html",
        products=products,
        product_stock_details=product_stock_details
    )


@views.route("/delete_category", methods=["POST"])
def delete_category():
    category_id = request.form.get("category_id")
    if category_id:
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
    return redirect(url_for("views.manage_categories"))


@views.route("/search_products", methods=["GET"])
def search_products():
    query = request.args.get("query", "")
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    return jsonify(
        [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "sale_price": product.sale_price,
                "description": product.description,
            }
            for product in products
        ]
    )


@views.route("/import_csv", methods=["POST"])
def import_csv():
    if "csv_file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("views.products"))

    file = request.files["csv_file"]

    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("views.products"))

    if file and file.filename.endswith(".csv"):
        filename = secure_filename(file.filename)
        file_path = f"uploads/{filename}"  # Adjust this path as needed
        file.save(file_path)

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("name")
                sku = row.get("sku")
                category = row.get("category")
                price = row.get("price")
                sale_price = row.get("sale_price")
                supplier = row.get("supplier")
                description = row.get("description")

                # Check for existing SKU
                existing_product = Product.query.filter_by(sku=sku).first()
                if existing_product:
                    # Update existing product
                    existing_product.name = name
                    existing_product.category = category
                    existing_product.price = float(price)
                    existing_product.sale_price = float(sale_price)
                    existing_product.supplier = supplier
                    existing_product.description = description
                else:
                    # Create new product
                    new_product = Product(
                        name=name,
                        sku=sku,
                        category=category,
                        price=float(price),
                        sale_price=float(sale_price),
                        supplier=supplier,
                        description=description,
                    )
                    db.session.add(new_product)

            db.session.commit()
            flash("Products imported successfully!", "success")

    else:
        flash("Invalid file format. Please upload a CSV file.", "danger")

    return redirect(url_for("views.products"))