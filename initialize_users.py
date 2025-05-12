from app import app, db, User, users, generate_password_hash
from datetime import datetime

def initialize_users():
    with app.app_context():
        # Check if users table has data
        if User.query.count() > 0:
            print("Users already exist in database")
            return
        
        # Add users from mock data
        for user_data in users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password'],  # This is already hashed in the mock data
                role=user_data['role'],
                created_at=user_data['created_at']
            )
            
            db.session.add(user)
            
        # Add an extra admin user just to be sure
        admin = User(
            username="webadmin",
            email="webadmin@example.com",
            role="admin",
            created_at=datetime.now()
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        db.session.commit()
        print("Users initialized successfully")

if __name__ == "__main__":
    initialize_users() 