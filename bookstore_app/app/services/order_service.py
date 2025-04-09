from app.models.db import get_db_connection

def create_order(customer_id, selected_books, quantities, prices):
    """
    Handles the business logic for creating an order.
    """
    total_amount = 0
    order_items = []

    for book_id, qty, price in zip(selected_books, quantities, prices):
        total_amount += qty * price
        order_items.append((book_id, qty))

    # Insert order into the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO orders (customer_id, order_date, total_amount) VALUES (%s, NOW(), %s) RETURNING order_id',
        (customer_id, total_amount)
    )
    order_id = cur.fetchone()[0]

    # Insert order items into the database
    for book_id, qty in order_items:
        cur.execute(
            'INSERT INTO order_items (order_id, book_id, quantity) VALUES (%s, %s, %s)',
            (order_id, book_id, qty)
        )

    conn.commit()
    conn.close()

    return order_id
