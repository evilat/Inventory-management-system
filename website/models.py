from datetime import datetime
from sqlalchemy.sql import func
from . import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)  # Stock Keeping Unit
    category = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    supplier = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Sale {self.id} for Product {self.product.name}>'

class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('stock_movements', lazy=True))
    change_quantity = db.Column(db.Integer, nullable=False)  # Positive for adding stock, negative for reducing stock
    movement_type = db.Column(db.String(50), nullable=False)  # e.g., 'Sale', 'Purchase', 'Adjustment'
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<StockMovement {self.movement_type} for Product {self.product.name}>'