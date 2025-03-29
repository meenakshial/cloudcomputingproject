from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy
from sqlalchemy import func
from models import db, StockItem, StockHistory  # Import models
from forms import StockForm
from reports import generate_stock_report
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockpilot.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

db.init_app(app)  # Now initialize SQLAlchemy with the app

# Create database tables within the app context
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    total_items = StockItem.query.count()
    low_stock_items = StockItem.query.filter(StockItem.quantity <= StockItem.low_stock_threshold).count()
    recent_history = StockHistory.query.order_by(StockHistory.date.desc()).limit(5).all()  #Recent History
    total_value = db.session.query(func.sum(StockItem.quantity * StockItem.purchase_price)).scalar() or 0.0 # Total Stock Value

    return render_template('index.html', total_items=total_items, low_stock_items=low_stock_items, recent_history=recent_history, total_value=total_value)


@app.route('/stock')
def stock_list():
    search_term = request.args.get('search', '')
    filter_threshold = request.args.get('filter_threshold', type=int)

    query = StockItem.query

    if search_term:
        query = query.filter(
            (StockItem.name.contains(search_term)) | (StockItem.description.contains(search_term)) | (StockItem.id.like(f"%{search_term}%")) #Search by ID
        )

    if filter_threshold is not None:
        query = query.filter(StockItem.quantity <= filter_threshold)

    items = query.all()
    return render_template('stock_list.html', items=items, search_term=search_term, filter_threshold=filter_threshold)


@app.route('/stock/add', methods=['GET', 'POST'])
def add_stock():
    form = StockForm()
    if form.validate_on_submit():
        new_item = StockItem(name=form.name.data, quantity=form.quantity.data, description=form.description.data, purchase_price=form.purchase_price.data, supplier=form.supplier.data, low_stock_threshold=form.low_stock_threshold.data)
        db.session.add(new_item)
        db.session.commit()
        flash('Stock item added successfully!', 'success') #Flash message
        return redirect(url_for('stock_list'))
    return render_template('add_stock.html', form=form)


@app.route('/stock/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_stock(item_id):
    item = StockItem.query.get_or_404(item_id)
    form = StockForm(obj=item)  # Populate form with item data
    if form.validate_on_submit():
        original_quantity = item.quantity
        item.name = form.name.data
        item.quantity = form.quantity.data
        item.description = form.description.data
        item.purchase_price = form.purchase_price.data
        item.supplier = form.supplier.data
        item.low_stock_threshold = form.low_stock_threshold.data

        quantity_change = item.quantity - original_quantity
        if quantity_change !=0:
            history_record = StockHistory(item_id=item.id, quantity_change=quantity_change, description=f"Quantity updated via edit form.") #History Tracking
            db.session.add(history_record)
        db.session.commit()
        flash('Stock item updated successfully!', 'success')
        return redirect(url_for('stock_list'))
    return render_template('edit_stock.html', form=form, item=item)


@app.route('/stock/delete/<int:item_id>')
def delete_stock(item_id):
    item = StockItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Stock item deleted successfully!', 'success')
    return redirect(url_for('stock_list'))

@app.route('/stock/history/<int:item_id>')
def stock_history(item_id):
    item = StockItem.query.get_or_404(item_id)
    history_items = StockHistory.query.filter_by(item_id=item_id).order_by(StockHistory.date.desc()).all()
    return render_template('history.html', item=item, history_items=history_items)


@app.route('/reports/stock_levels')
def generate_report():
    items = StockItem.query.all()
    csv_data = generate_stock_report(items)
    return send_file(csv_data, mimetype='text/csv', as_attachment=True, download_name='stock_report.csv')


if __name__ == '__main__':
    app.run(debug=True)