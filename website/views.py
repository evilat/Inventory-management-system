import csv, io, os, json
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify, abort
from werkzeug.utils import secure_filename
from .models import Product, Category, StockMovement
from .utils import load_config
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
            if movement.movement_type == "addition":
                current_quantity += movement.change_quantity
            elif movement.movement_type == "removal":
                current_quantity -= movement.change_quantity

        current_quantities[product.id] = current_quantity

    products = products[::-1]
    categories = Category.query.all()

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        selected_category=selected_category,
        current_quantities=current_quantities,
    )


@views.route("/edit_product", methods=["GET", "POST"])
@views.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id=None):
    categories = Category.query.all()
    config = load_config()
    default_category = config.get("default_category")

    if product_id:
        product = Product.query.get_or_404(product_id)
        if request.method == "POST":
            product.name = request.form.get("name")
            product.sku = request.form.get("sku")
            product.category = request.form.get("category")
            product.price = float(request.form.get("price"))
            sale_price = request.form.get("sale_price")
            product.sale_price = float(sale_price) if sale_price else None
            product.supplier = request.form.get("supplier")
            product.description = request.form.get("description")
            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("views.products"))
        return render_template("edit_product.html", product=product, categories=categories)

    else:
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

        # Set the default category for new products
        if not request.form.get("category"):
            selected_category = default_category
        return render_template("edit_product.html", product=None, categories=categories, selected_category=default_category)


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
    config = load_config()
    default_category_name = config.get('default_category')

    if request.method == "POST":
        category_name = request.form.get("category_name")
        if not category_name:
            flash("Category name is required.", "danger")
        elif category_name == default_category_name:
            flash("Cannot create a category with the default category name.", "danger")
        elif Category.query.filter_by(name=category_name).first():
            flash("Category already exists.", "danger")
        else:
            # Add new category
            new_category = Category(name=category_name, is_deletable=True)
            db.session.add(new_category)
            db.session.commit()
            flash("Category added successfully!", "success")
        
        return redirect(url_for("views.manage_categories"))

    categories = Category.query.all()
    return render_template("manage_categories.html", categories=categories)


@views.route("/delete_category", methods=["POST"])
def delete_category():
    category_id = request.form.get("category_id")
    if category_id:
        category = Category.query.get(category_id)
        if category and category.is_deletable:
            db.session.delete(category)
            db.session.commit()
        else:
            flash("Cannot delete the default category.", "danger")
    return redirect(url_for("views.manage_categories"))


@views.route("/manage_stock", methods=["GET", "POST"])
def manage_stock():
    config = load_config()

    if not config.get("enable_stock_management", False):
        flash("Stock management is disabled.", "danger")
        return redirect(url_for("views.home"))
    
    if request.method == "POST":
        product_id = request.form.get("product_id")
        change_quantity = int(request.form.get("change_quantity"))
        movement_type = request.form.get("movement_type")
        description = request.form.get("description")

        if movement_type not in ["addition", "removal"]:
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
            if movement.movement_type == "addition":
                current_quantity += movement.change_quantity
            elif movement.movement_type == "removal":
                current_quantity -= movement.change_quantity

        # Convert StockMovement objects to dictionaries
        stock_movement_list = [
            {
                "change_quantity": movement.change_quantity,
                "movement_type": movement.movement_type,
                "movement_date": movement.movement_date.strftime("%Y-%m-%d %H:%M:%S"),
                "description": movement.description,
            }
            for movement in stock_movements
        ]

        product_stock_details[product.id] = {
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "sale_price": product.sale_price,
            "description": product.description,
            "current_quantity": current_quantity,
            "stock_movements": stock_movement_list,
        }

    return render_template(
        "manage_stock.html",
        products=products,
        product_stock_details=product_stock_details,
    )


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
        file_content = file.read().decode("utf-8")
        csvfile = io.StringIO(file_content)
        reader = csv.DictReader(csvfile)

        # Get default category from the config
        config = load_config()
        default_category_name = config.get("default_category", "Default")

        for row in reader:
            name = row.get("name")
            sku = row.get("sku")
            category = row.get("category")
            price = row.get("price")
            sale_price = row.get("sale_price")
            supplier = row.get("supplier")
            description = row.get("description")

            # Check and update category
            if category:
                existing_category = Category.query.filter_by(name=category).first()
                if not existing_category:
                    # Set the category to default if it doesn't exist
                    category = default_category_name

            # Check for existing SKU
            existing_product = Product.query.filter_by(sku=sku).first()
            if existing_product:
                # Update existing product
                existing_product.name = name
                existing_product.category = category
                existing_product.price = float(price)
                existing_product.sale_price = float(sale_price) if sale_price else None
                existing_product.supplier = supplier
                existing_product.description = description
            else:
                # Create new product
                new_product = Product(
                    name=name,
                    sku=sku,
                    category=category,
                    price=float(price),
                    sale_price=float(sale_price) if sale_price else None,
                    supplier=supplier,
                    description=description,
                )
                db.session.add(new_product)

        db.session.commit()
        flash("Products imported successfully!", "success")

    else:
        flash("Invalid file format. Please upload a CSV file.", "danger")

    return redirect(url_for("views.products"))


@views.route("/settings", methods=["GET", "POST"])
@views.route("/settings/<section>", methods=["GET", "POST"])
def settings(section='products'):
    CONFIG_PATH = os.path.join("userdata", "config.json")

    def load_config():
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return {}

    def save_config(config):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)

    config = load_config()

    if request.method == "POST":
        enable_stock_management = "true" in request.form.get("enableStockManagement", "false")
        low_stock_threshold = request.form.get("lowStockThreshold")

        config["enable_stock_management"] = enable_stock_management
        if enable_stock_management and low_stock_threshold.isdigit():
            config["low_stock_threshold"] = int(low_stock_threshold)
        
        default_category = request.form.get("defaultCategory")
        if default_category:
            config["default_category"] = default_category
            
            # Check for an existing non-deletable category
            existing_category = Category.query.filter_by(is_deletable=False).first()
            if existing_category:
                existing_category.name = default_category
            else:
                # Create a new non-deletable category
                new_category = Category(name=default_category, is_deletable=False)
                db.session.add(new_category)
                
            db.session.commit()

        save_config(config)
        flash("Settings saved successfully!", "success")
        return redirect(url_for('views.settings', section=section))

    return render_template("settings.html", config=config, section=section)


@views.context_processor
def inject_config():
    config = load_config()
    return dict(config=config)
