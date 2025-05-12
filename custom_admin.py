from app import app, db, User

# Create admin user with custom password
def create_custom_admin():
    with app.app_context():
        username = 'somilpandey'
        password = 'somil123'
        
        # Check if admin already exists
        admin = User.query.filter_by(username=username).first()
        if admin:
            print(f"Admin user {username} already exists")
            # Update password anyway
            admin.set_password(password)
            db.session.commit()
            print(f"Updated password for {username}")
            return
        
        # Create new admin user
        admin = User(
            username=username,
            email=f'{username}@example.com',
            role='admin'
        )
        admin.set_password(password)
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {username} created successfully with custom password")
        print(f"Login with: Username: {username}, Password: {password}")

if __name__ == "__main__":
    create_custom_admin() 