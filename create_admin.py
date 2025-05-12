from app import app, db, User

# Create admin user
def create_admin_user():
    with app.app_context():
        # Check if somilpandey05 admin already exists
        admin = User.query.filter_by(username='somilpandey05').first()
        if admin:
            print("Admin user somilpandey05 already exists")
            return
        
        # Create new admin user
        admin = User(
            username='somilpandey05',
            email='somilpandey05@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        print("Admin user somilpandey05 created successfully")

if __name__ == "__main__":
    create_admin_user() 