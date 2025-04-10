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
        decrease_quantity(book_id, qty)  # Decrease stock quantity

    # Insert order into the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO orders (customer_id, order_date, total_amount) VALUES (%s, NOW(), %s) RETURNING order_id',
        (customer_id, total_amount)
    )
    
    # Fetch the generated order_id
    # This assumes that the order_id is the first column in the returned row.
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

def create_order1(customer_id, order_items):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert the order
        query = "INSERT INTO orders (customer_id, order_date) VALUES (%s, NOW()) RETURNING order_id;"
        cursor.execute(query, (customer_id,))
        order_id = cursor.fetchone()[0]  # Get the newly created order_id
        
        # Add each item to the order
        for item in order_items:
            book_id = item['book_id']
            quantity = item['quantity']
            price = item['price']
            
            # Insert the order item
            query = """
            INSERT INTO order_items (order_id, book_id, quantity)
            VALUES (%s, %s, %s);
            """
            cursor.execute(query, (order_id, book_id, quantity))
            
            # Update the stock quantity
            update_stock_quantity(book_id, quantity)
        
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        return order_id  # Return the order_id for reference
    
    except Exception as e:
        print(f"Error creating order: {e}")
        return None

def update_stock_quantity(book_id, quantity_purchased):
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update the stock quantity
        query = """
        UPDATE books 
        SET stock_quantity = stock_quantity - %s
        WHERE book_id = %s AND stock_quantity >= %s;
        """
        cursor.execute(query, (quantity_purchased, book_id, quantity_purchased))
        
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        # Handle any errors that occur during the update
        print(f"Error updating stock quantity: {e}")
        return False

# Update quantity function (sets a specific stock value)
def update_quantity(book_id, new_quantity):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update stock to a new value
        query = """
        UPDATE books 
        SET stock_quantity = %s
        WHERE book_id = %s;
        """
        cursor.execute(query, (new_quantity, book_id))
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating stock quantity: {e}")
        return False
    
# Decrease quantity function
def decrease_quantity(book_id, quantity):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Decrease stock
        query = """
        UPDATE books 
        SET stock_quantity = stock_quantity - %s
        WHERE book_id = %s AND stock_quantity >= %s;
        """
        cursor.execute(query, (quantity, book_id, quantity))
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error decreasing stock quantity: {e}")
        return False

# Increase quantity function
def increase_quantity(book_id, quantity):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Increase stock
        query = """
        UPDATE books 
        SET stock_quantity = stock_quantity + %s
        WHERE book_id = %s;
        """
        cursor.execute(query, (quantity, book_id))
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error increasing stock quantity: {e}")
        return False
