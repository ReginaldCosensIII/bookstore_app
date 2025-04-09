import psycopg2
import datetime
import bcrypt
import pwinput

DATABASE_URL = "postgresql://admin:plAA1t13QVCmkRQFr2bGoAbpJNLeKUrQ@dpg-cvqllt49c44c73bgi16g-a.virginia-postgres.render.com/bookstore_db_40si"
# --- Database connection setup ---
try:
    """""
    conn = psycopg2.connect(
    host="localhost",
    database="bookstore_db",
    user="postgres",      # <-- Replace with your PostgreSQL username
    password="Bigpimp",   # <-- Replace with your PostgreSQL password
    port="5433"                # Update this to the correct port
    )"""
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    print("✅ Connected to the database!")
    
except Exception as e:
    
    print("❌ Failed to connect:", e)
    
    exit()

def login():
        
    username = input("Username: ").strip().lower()  # Convert to lowercase
    password = pwinput.pwinput(prompt="Password: ")  # Shows asterisks

    cursor.execute("SELECT user_id, username, password, role FROM users WHERE LOWER(username) = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        
        print(f"✅ Logged in as {user[1]} ({user[3]})")
        
        return {'user_id': user[0], 'username': user[1], 'role': user[3]}
    else:
        
        print("❌ Invalid username or password.")
        
        return None
    
def create_order():
    
    try:
        
        print("\n--- Create Order ---")        
        customer_id = input("Enter customer ID: ")
        order_items = []

        while True:
            
            book_id = input("Enter book ID to add to order (or 'done' to finish): ")
            
            if book_id.lower() == 'done':
                
                break
            
            quantity = int(input("Enter quantity: "))

            # Check stock
            cursor.execute("SELECT title, price, stock_quantity FROM books WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                
                print("Book not found.")
                
                continue
            
            title, price, stock_quantity = book

            if quantity > stock_quantity:
                
                print(f"Not enough stock for '{title}'. Only {stock_quantity} available.")
                
                continue

            order_items.append((book_id, title, price, quantity))

        if not order_items:
            
            print("No items added to the order.")
            
            return

        # Calculate total
        total_amount = sum(price * quantity for _, _, price, quantity in order_items)
        order_date = datetime.datetime.now()

        # Insert into orders
        cursor.execute("""
            INSERT INTO orders (customer_id, order_date, total_amount)
            VALUES (%s, %s, %s) RETURNING order_id
        """, (customer_id, order_date, total_amount))
        
        order_id = cursor.fetchone()[0]

        # Insert into order_items and update stock
        for book_id, title, price, quantity in order_items:
            
            cursor.execute("""
                INSERT INTO order_items (order_id, book_id, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, book_id, quantity))

            cursor.execute("""
                UPDATE books SET stock_quantity = stock_quantity - %s WHERE book_id = %s
            """, (quantity, book_id))

        conn.commit()
        print(f"Order {order_id} created successfully with total: ${total_amount:.2f}")

    except Exception as e:
        
        conn.rollback()
        print("Error creating order:", e)

def create_user():
    
    if current_user['role'] != 'admin':
        
        print("❌ Only admins can create users.")
        
        return

    username = input("Enter new username: ").strip().lower()  # Convert to lowercase

    # Check for duplicate username
    cursor.execute("SELECT username FROM users WHERE LOWER(username) = %s", (username,))
        
    while cursor.fetchone():
        
        print("❌ Username already exists. Choose another.")
        
        username = input("Enter new username: ").strip().lower()  # Convert to lowercase

        # Check for duplicate username
        cursor.execute("SELECT username FROM users WHERE LOWER(username) = %s", (username,))
        
    # Masked password input with confirmation
    password = pwinput.pwinput("Enter new password: ")
    confirm = pwinput.pwinput("Confirm password: ")

    while password != confirm:
        
        print("❌ Passwords do not match. User not created.")
        
        # Masked password input with confirmation
        password = pwinput.pwinput("Enter new password: ")
        confirm = pwinput.pwinput("Confirm password: ")

    role = input("Role (admin/user): ").strip().lower()

    while role not in ['admin', 'user']:
        
        print("❌ Invalid role. Must be 'admin' or 'user'.")
        
        role = input("Role (admin/user): ").strip().lower()

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (username, hashed, role))
        conn.commit()
        
        print(f"✅ User '{username}' created successfully.")
        
    except Exception as e:
        
        print(f"❌ Failed to create user: {e}")

def change_password():
    
    print("\n--- Change Password ---")
    
    if current_user['role'] != 'admin':
        # Step 1: Prompt for current password
        current_password = pwinput.pwinput("Enter current password: ")
    
        # Step 2: Verify current password
        cursor.execute("SELECT password FROM users WHERE user_id = %s", (current_user['user_id'],))
        stored_password = cursor.fetchone()[0]
    
        while not bcrypt.checkpw(current_password.encode('utf-8'), stored_password.encode('utf-8')):
        
            print("❌ Incorrect current password.")
        
            # Step 1: Prompt for current password
            current_password = pwinput.pwinput("Enter current password: ")
            
            if current_password == "exit":
                
                print("Exiting password change.")
                
                return
            
            # Step 2: Verify current password
            cursor.execute("SELECT password FROM users WHERE user_id = %s", (current_user['user_id'],))
            stored_password = cursor.fetchone()[0]
            
    if current_user['role'] == 'admin':
        
        change_pass_userid = input("Change password to what user ID: ")
    
    # Step 3: Prompt for new password
    new_password = pwinput.pwinput("Enter new password: ")
    
    # Step 4: Confirm new password
    confirm_password = pwinput.pwinput("Confirm new password: ")
    
    while new_password != confirm_password:
        
        print("❌ Passwords do not match. Please try again.")
        
        # Step 3: Prompt for new password
        new_password = pwinput.pwinput("Enter new password: ")
    
        # Step 4: Confirm new password
        confirm_password = pwinput.pwinput("Confirm new password: ")

    # Step 5: Hash new password
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update password in the database
    if current_user['role'] == 'admin':
        
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed_new_password, change_pass_userid))
    
    else:
        
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed_new_password, current_user['user_id']))
    
    conn.commit()

    print("✅ Password updated successfully.")        

def view_users():
    
    if current_user['role'] != 'admin':
        
        print("❌ Only admins can view user information.")
        
        return

    print("\n--- 👥 View Users ---")
    print("1. View all users")
    print("2. View only admin users")
    print("3. View only regular users")

    choice = input("Enter choice: ")
    
    while choice not in ["1", "2", "3"]:
        
        print("❌ Invalid choice. Please try again.")
        print("\n--- 👥 View Users ---")
        print("1. View all users")
        print("2. View only admin users")
        print("3. View only regular users")

        choice = input("Enter choice: ")
    
    if choice == "1":
        
        query = "SELECT user_id, username, role FROM users ORDER BY user_id"
        label = "All Users"
        
    elif choice == "2":
        
        query = "SELECT user_id, username, role FROM users WHERE role = 'admin' ORDER BY user_id"
        label = "Admin Users"
        
    elif choice == "3":
        
        query = "SELECT user_id, username, role FROM users WHERE role = 'user' ORDER BY user_id"
        label = "Regular Users"
        
    try:
        
        cursor.execute(query)
        users = cursor.fetchall()

        if users:
            
            print(f"\n--- {label} ---")
            
            for user in users:
                
                print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
                
        else:
            
            print("No users found.")
            
    except Exception as e:
        
        print(f"❌ Error retrieving users: {e}")

def view_order(order_id):
    
    try:
        # Fetch order summary
        cursor.execute("""
            SELECT order_id, customer_id, order_date, total_amount
            FROM orders
            WHERE order_id = %s
        """, (order_id,))
        
        order = cursor.fetchone()

        if not order:
            
            print(f"❌ Order with ID {order_id} not found.")
            return

        print("\n🧾 Order Summary:")
        print(f"Order ID: {order[0]}")
        print(f"Customer ID: {order[1]}")
        print(f"Order Date: {order[2]}")
        print(f"Total Amount: ${order[3]:.2f}")

        # Fetch order items with book info
        cursor.execute("""
            SELECT oi.book_id, b.title, b.author, oi.quantity
            FROM order_items oi
            JOIN books b ON oi.book_id = b.book_id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        items = cursor.fetchall()

        print("\n📚 Items in Order:")
        
        for item in items:
            
            print(f"- Book ID: {item[0]}, Title: {item[1]}, Author: {item[2]}, Quantity: {item[3]}")

    except Exception as e:
        
        print(f"⚠️ Error retrieving order: {e}")
        
def view_orders():
    
    try:
        
        cursor.execute("""
            SELECT order_id, customer_id, order_date, total_amount
            FROM orders
            ORDER BY order_date DESC
        """)
        
        orders = cursor.fetchall()

        if not orders:
            
            print("📭 No orders found in the system.")
            return

        print("\n📦 All Orders:")
        
        for order in orders:
            
            print(f"- Order ID: {order[0]}, Customer ID: {order[1]}, Date: {order[2]}, Total: ${order[3]:.2f}")
            
    except Exception as e:
        
        print(f"⚠️ Error retrieving orders: {e}")

def view_customer(customer_id):
    
    try:
        
        query = "SELECT * FROM customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if customer:
            
            print("\n📄 Customer Information:")
            colnames = [desc[0] for desc in cursor.description]
            for col, val in zip(colnames, customer):
                print(f"{col}: {val}")
        else:
            
            print("❌ Customer not found.")

    except Exception as e:
        
        print(f"❌ Error viewing customer: {e}")

def view_customers():
    
    try:
        
        query = "SELECT * FROM customers"
        cursor.execute(query)
        customers = cursor.fetchall()

        if customers:
            
            print("\n📄 All Customers:")
            colnames = [desc[0] for desc in cursor.description]
            
            for customer in customers:
                
                print("-" * 40)
                
                for col, val in zip(colnames, customer):
                    
                    print(f"{col}: {val}")
                    
        else:
            
            print("⚠️ No customers found.")

    except Exception as e:
        print(f"❌ Error viewing customers: {e}")

def search_books():
    
    # Prompt the user for search type
    print("Search by:")
    print("1.   Title")
    print("2.   Author")
    print("3.   Genre")
    print("4.   Book ID")
    
    search_type = input("Enter the number corresponding to your choice: ")

    # Based on the user's choice, prompt for a search term
    if search_type == "1":
        
        searchre_term = input("Enter the book title: ")
        query = "SELECT * FROM books WHERE title ILIKE %s"
        
    elif search_type == "2":
        
        search_term = input("Enter the author name: ")
        query = "SELECT * FROM books WHERE author ILIKE %s"
        
    elif search_type == "3":
        
        search_term = input("Enter the genre: ")
        query = "SELECT * FROM books WHERE genre ILIKE %s"
        
    elif search_type == "4":
        
        search_term = input("Enter the book ID: ")
        query = "SELECT * FROM books WHERE book_id = %s"
        
    else:
        
        print("Invalid choice. Returning to menu.")
        
        return

    # Perform the query and display results
    try:
        
        if search_type == "4":
            
            # Book ID search doesn't need wildcards
            cursor.execute(query, (search_term,))
            
        else:
            
            # Use wildcards for title, author, and genre searches
            cursor.execute(query, ('%' + search_term + '%',))  
        
        books = cursor.fetchall()

        if books:
            
            print(f"\nBooks matching '{search_term}':\n")
            
            for book in books:
                
                print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Price: ${book[3]}, Stock: {book[4]}, Genre: {book[5]}")
                
        else:
            
            print(f"No books found for '{search_term}'.")

    except Exception as e:
        
        print(f"Error occurred: {e}")


def view_book(book_id):
    
    query = "SELECT * FROM books WHERE book_id = %s"
    cursor.execute(query, (book_id,))
    book = cursor.fetchone()
    
    if book:
        
        print("📖 Book found:", book)
        
    else:
        
        print("❌ Book not found.")

def view_books():
    
    cursor.execute("SELECT * FROM books ORDER BY book_id")
    books = cursor.fetchall()
    
    print("\n📘 Book List:")
    
    for book in books:
        
        print(book)

def update_stock(book_id, new_stock):
    
    query = "UPDATE books SET stock_quantity = %s WHERE book_id = %s"
    cursor.execute(query, (new_stock, book_id))
    conn.commit()
    
    print("🔄 Stock updated.")

def delete_book(book_id):
    
    query = "DELETE FROM books WHERE book_id = %s"
    cursor.execute(query, (book_id,))
    conn.commit()
    
    print("❌ Book deleted.")

# --- CLI Menu ---
def menu():
    
    run = True
    
    while run:
        
        if current_user['role'] == 'admin':
            
            print("\n--- 📖 Bookstore Manager (Admin) ---")
            print("1.   Add Book")
            print("2.   View Books")
            print("3.   View Books by Title, Author, Genre, or ID")
            print("4.   Update Stock")
            print("5.   Delete Book")
            print("6.   Create User")
            print("7.   Change Password")
            print("8.   View Users")
            print("9.   View Order by order ID")
            print("10.  View Orders")
            print("11.  View Customer by customer ID")
            print("12.  View Customers")
            print("13.  Create Order")
            print("14.  Exit")
        
            choice = input("Enter choice: ")

            if choice == "1":
                                
                title = input("Title: ")
                author = input("Author: ")
                genre = input("Genre (leave blank for 'Unknown'): ") or "Unknown"
                price = float(input("Price (default 19.99): ") or 19.99)
                stock = int(input("Stock Quantity (default 1): ") or 1)
                
                add_book(title, author, genre, price, stock)
            
            elif choice == "2":
                
                view_books()
                
            elif choice == "3":
                
                search_books()
                            
            elif choice == "4":
                
                book_id = int(input("Book ID to update stock: "))
                stock = int(input("New stock quantity: "))
                
                update_stock(book_id, stock)
                
            elif choice == "5":
                
                book_id = int(input("Book ID to delete: "))
                
                delete_book(book_id)
                
            elif choice == "6":
                
                create_user()          
                                
            elif choice == "7":
                
                change_password()   
                
            elif choice == "8":
                
                view_users()       
                                  
            elif choice == "9":
                
                order_id = int(input("Enter Order ID to view: "))
                view_order(order_id)
                                        
            elif choice == "10":
                
                view_orders()
            
            elif choice == "11":
                
                customer_id = input("Enter Customer ID to view: ")
                view_customer(customer_id)
            
            elif choice == "12":
                
                view_customers()            
            
            elif choice == "13":
                
                create_order()
                                        
            elif choice == "14":
                
                print("👋 Goodbye!")
                
                run = False
                
            else:
                
                print("❌ Invalid choice. Please try again.")
                
        elif current_user['role'] == 'user':
            
            print("\n--- 📖 Bookstore Manager (User) ---")
            print("1.   Add Book")
            print("2.   View Books")
            print("3.   Search Books (Title, Author, Genre, or ID)")
            print("4.   Update Stock")
            print("5.   Delete Book")
            print("6.   Change Password")
            print("7.   Exit")
        
            choice = input("Enter choice: ")

            if choice == "1":
                
                title = input("Title: ")
                author = input("Author: ")
                genre = input("Genre (leave blank for 'Unknown'): ") or "Unknown"
                price = float(input("Price (default 19.99): ") or 19.99)
                stock = int(input("Stock Quantity (default 1): ") or 1)
                
                add_book(title, author, genre, price, stock)
            
            elif choice == "2":
                
                view_books()
                
            elif choice == "3":
                
                search_books()
                            
            elif choice == "4":
                
                book_id = int(input("Book ID to update stock: "))
                stock = int(input("New stock quantity: "))
                
                update_stock(book_id, stock)
                
            elif choice == "5":
                
                book_id = int(input("Book ID to delete: "))
                
                delete_book(book_id)
                
            elif choice == "6":
                
                change_password()             
                                
            elif choice == "7":
                
                print("👋 Goodbye!")
                
                run = False
                
            else:
                
                print("❌ Invalid choice. Please try again.")

current_user = login()

if not current_user:
    
    print("❌ Login failed. Exiting...")
    
    exit()

menu()

# --- Close connection ---
cursor.close()
conn.close()