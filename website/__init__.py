from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.secret_key = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    db.init_app(app)

    from .views import views
    app.register_blueprint(views, url_prefix='/')

    from .models import Product, Sale, StockMovement

    with app.app_context():
        db.create_all()

    return app