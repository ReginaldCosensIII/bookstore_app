class Book:
    
    def __init__(self, book_id, title, author, genre, price, stock_quantity):
        
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.price = price
        self.stock_quantity = stock_quantity

    def is_in_stock(self):
        
        return self.stock_quantity > 0

    def __str__(self):
        
        return (f"Book ID: {self.book_id}, Title: {self.title}, Author: {self.author}, "
                f"Genre: {self.genre}, Price: ${self.price:.2f}, Stock: {self.stock_quantity}")
