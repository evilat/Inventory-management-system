from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Name is required"), Length(max=100)])
    sku = StringField('SKU', validators=[DataRequired(message="SKU is required"), Length(max=50)])
    category = StringField('Category', validators=[DataRequired(message="Category is required"), Length(max=50)])
    price = FloatField('Price', validators=[DataRequired(message="Price is required"), NumberRange(min=0, message="Price must be positive")])
    quantity = IntegerField('Quantity', validators=[DataRequired(message="Quantity is required"), NumberRange(min=0, message="Quantity must be positive")])
    supplier = StringField('Supplier', validators=[DataRequired(message="Supplier is required"), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(message="Description is required")])