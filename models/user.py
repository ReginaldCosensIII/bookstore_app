class User:
    
    def __init__(self, user_id, username, role, created_at):
        
        self.user_id = user_id
        self.username = username
        self.role = role
        self.created_at = created_at

    def is_admin(self):
        
        return self.role == 'admin'

    def __str__(self):
        
        return f"User ID: {self.user_id}, Username: {self.username}, Role: {self.role}, Created At: {self.created_at}"
