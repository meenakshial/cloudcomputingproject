from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  # Initialize SQLAlchemy without passing app yet

class StockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    purchase_price = db.Column(db.Float)
    supplier = db.Column(db.String(100))
    low_stock_threshold = db.Column(db.Integer, default=5)  # Default low stock threshold
    history = db.relationship('StockHistory', backref='item', lazy=True)

    def __repr__(self):
        return f"StockItem(id={self.id}, name='{self.name}', quantity={self.quantity})"

class StockHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_item.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantity_change = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))  # Explanation of the change

    def __repr__(self):
        return f"StockHistory(id={self.id}, item_id={self.item_id}, date={self.date}, quantity_change={self.quantity_change})"