from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class StockForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description')
    purchase_price = FloatField('Purchase Price')
    supplier = StringField('Supplier')
    low_stock_threshold = IntegerField('Low Stock Threshold', default=5)
    submit = SubmitField('Submit')