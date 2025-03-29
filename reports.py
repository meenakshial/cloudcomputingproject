import csv
from io import StringIO

def generate_stock_report(items):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Quantity', 'Description', 'Purchase Price', 'Supplier'])  # Header

    for item in items:
        writer.writerow([item.id, item.name, item.quantity, item.description, item.purchase_price, item.supplier])

    return output.getvalue()