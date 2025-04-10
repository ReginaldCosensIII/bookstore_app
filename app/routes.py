from flask import Blueprint, render_template, request, redirect, url_for
from app.services.order_service import create_order  # Import the service
from app.models.db import get_db_connection

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books;')
    books = cur.fetchall()
    conn.close()
    return render_template('index.html', books=books)

@bp.route('/create_order', methods=['POST'])
def create_order_route():
    customer_id = request.form.get("customer_id")
    
    if not customer_id or customer_id.strip() == "":
        customer_id = 1
    else:
        customer_id = int(customer_id)
    
    selected_books = request.form.getlist('selected_books')
    quantities = [int(request.form.get(f'quantity_{book_id}', 1)) for book_id in selected_books]
    prices = [float(request.form.get(f'price_{book_id}', 0.0)) for book_id in selected_books]
    
    # Use the order service to create the order
    create_order(customer_id, selected_books, quantities, prices)
    
    return redirect(url_for('main.index'))
