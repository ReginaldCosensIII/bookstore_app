from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Database connection
def get_db_connection():
    
    DATABASE_URL = os.environ.get("DATABASE_URL")
    return psycopg2.connect(DATABASE_URL)
    return conn

# Route to view books
@app.route('/')

def index():
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books;')  # Assuming books table has title, author, price, etc.
    books = cur.fetchall()
    conn.close()
    
    return render_template('index.html', books=books)

@app.route('/create_order', methods=['POST'])

def create_order():
    
    customer_id = request.form.get("customer_id")

    if not customer_id or customer_id.strip() == "":
        
        customer_id = 1  # default to 1 if nothing entered
    else:
        
        customer_id = int(customer_id)
        
    selected_books = request.form.getlist('selected_books')
    total_amount = 0
    order_items = []

    for book_id in selected_books:
        
        qty = int(request.form.get(f'quantity_{book_id}', 1))
        price = float(request.form.get(f'price_{book_id}', 0.0))
        total_amount += qty * price
        order_items.append((book_id, qty))

    # Insert order into the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO orders (customer_id, order_date, total_amount) VALUES (%s, NOW(), %s) RETURNING order_id',
        (1, total_amount)
    )
    order_id = cur.fetchone()[0]

    for book_id, qty in order_items:
        
        cur.execute(
            'INSERT INTO order_items (order_id, book_id, quantity) VALUES (%s, %s, %s)',
            (order_id, book_id, qty)
        )

    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
