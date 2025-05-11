from flask_sqlalchemy import SQLAlchemy
import os
import pymysql

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Initialize the database and create tables"""
    # First create the database if it doesn't exist
    try:
        conn = pymysql.connect(host='localhost', user='root', password='')
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS mango")
        conn.commit()
        cursor.close()
        conn.close()
        print("Database 'mango' created or already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
    
    # Configure and initialize SQLAlchemy with app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/mango'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Import models after db initialization to avoid circular imports
    from models import User, Product, Category, Order, OrderItem, Cart, CartItem, Review
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if categories already exist
        if Category.query.count() == 0:
            # Add default categories
            categories = [
                Category(name="Alphonso", description="The king of mangoes, known for its rich, creamy, delicate, and non-fibrous pulp."),
                Category(name="Kesar", description="Known for its bright orange pulp and sweet taste."),
                Category(name="Langra", description="Fiber-less, sweet and aromatic mangoes."),
                Category(name="Chausa", description="Sweet and juicy mangoes with a pleasant aroma."),
                Category(name="Banganapalli", description="Known for its sweetness, flavor and fiber-less pulp."),
                Category(name="Totapuri", description="Tangy and mild sweet flavor, often used for pickles and chutneys."),
                Category(name="Himsagar", description="Fiber-less, sweet and aromatic mangoes from West Bengal.")
            ]
            db.session.add_all(categories)
            db.session.commit()
            print("Added default categories.")
        
        # Add sample products if none exist
        if Product.query.count() == 0:
            # Get categories
            alphonso = Category.query.filter_by(name="Alphonso").first()
            kesar = Category.query.filter_by(name="Kesar").first()
            
            # Add sample products
            products = [
                Product(
                    name="Premium Alphonso Mangoes",
                    description="Premium quality Alphonso mangoes from Ratnagiri, Maharashtra. Box of 12 mangoes.",
                    price=1200.00,
                    stock=50,
                    image="alphonso_premium.jpg",
                    category_id=alphonso.id
                ),
                Product(
                    name="Regular Alphonso Mangoes",
                    description="Regular quality Alphonso mangoes from Devgad, Maharashtra. Box of 12 mangoes.",
                    price=900.00,
                    stock=100,
                    image="alphonso_regular.jpg",
                    category_id=alphonso.id
                ),
                Product(
                    name="Kesar Mangoes",
                    description="Sweet and aromatic Kesar mangoes from Gujarat. Box of 12 mangoes.",
                    price=800.00,
                    stock=75,
                    image="kesar.jpg",
                    category_id=kesar.id
                )
            ]
            db.session.add_all(products)
            db.session.commit()
            print("Added sample products.")
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    init_db(app) 