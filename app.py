from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import pymysql
from werkzeug.utils import secure_filename
from functools import wraps

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration - use environment variable for production
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://u483781610_Luciferr:Somilpandey123%23@srv1495.hstgr.io:3306/u483781610_yaswantt'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Handle static files in production
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Make some functions available to templates
@app.context_processor
def utility_processor():
    return {
        'get_user_role': get_user_role
    }

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.String(20), default='pending')
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, confirmed, delivered, cancelled
    notes = db.Column(db.Text)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending') # pending, paid
    shipping_address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    
    # Add relationships
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    product = db.relationship('Product', backref=db.backref('bookings', lazy=True))

# Create database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Admin authentication
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or User.query.get(session['user_id']).role != 'admin':
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role='customer'
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    total_customers = User.query.filter_by(role='customer').count()
    total_products = Product.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    top_products = Product.query.order_by(Product.stock.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         total_customers=total_customers,
                         total_products=total_products,
                         recent_orders=recent_orders,
                         top_products=top_products)

# Mock data for demonstration
product_list = [
    {
        'id': 1,
        'name': 'Alphonso Mango',
        'category_id': 1,
        'description': 'Premium Alphonso mangoes from Ratnagiri, Maharashtra.',
        'price': 1500,
        'stock': 50,
        'image': 'alphanso.jpg',
        'is_in_season': True
    },
    {
        'id': 2,
        'name': 'Kesar Mango',
        'category_id': 1,
        'description': 'Sweet and aromatic Kesar mangoes from Gujarat.',
        'price': 1200,
        'stock': 40,
        'image': 'kesar.jpg',
        'is_in_season': True
    },
    {
        'id': 3,
        'name': 'Rajapuri Mango',
        'category_id': 1,
        'description': 'Juicy Rajapuri mangoes from South India.',
        'price': 1000,
        'stock': 35,
        'image': 'rajapuri mango.jpg',
        'is_in_season': True
    },
    {
        'id': 4,
        'name': 'Payri Mango',
        'category_id': 1,
        'description': 'Sweet Payri mangoes from Maharashtra.',
        'price': 1200,
        'stock': 30,
        'image': 'mango.jpg',
        'is_in_season': True
    }
]

categories = [
    {
        'id': 1,
        'name': 'Fresh Mangoes',
        'description': 'Freshly harvested mangoes from different regions of India'
    },
    {
        'id': 2,
        'name': 'Mango Products',
        'description': 'Products made from mangoes like pickle, juice, etc.'
    }
]

users = [
    {
        'id': 1,
        'username': 'admin',
        'password': generate_password_hash('admin123'),
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_admin': True,
        'role': 'admin',
        'created_at': datetime(2023, 1, 1),
        'orders': []
    },
    {
        'id': 2,
        'username': 'customer',
        'password': generate_password_hash('user123'),
        'email': 'customer@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'is_admin': False,
        'role': 'customer',
        'created_at': datetime(2023, 2, 15),
        'orders': [1, 3]
    }
]

orders = [
    {
        'id': 1,
        'customer_id': 2,
        'order_date': datetime(2023, 4, 15),
        'total_amount': 1098,
        'status': 'Delivered',
        'payment_method': 'Credit Card',
        'payment_status': 'Completed',
        'shipping_address': '123 Main St',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001',
        'phone': '9876543210'
    },
    {
        'id': 2,
        'customer_id': 2,
        'order_date': datetime(2023, 5, 20),
        'total_amount': 950,
        'status': 'Processing',
        'payment_method': 'PayTM',
        'payment_status': 'Completed',
        'shipping_address': '456 Park Ave',
        'city': 'Delhi',
        'state': 'Delhi',
        'pincode': '110001',
        'phone': '8765432109'
    }
]

# Helper functions
def get_user_by_id(user_id):
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def get_user_role(user_id):
    user = User.query.get(user_id)
    if user:
        return user.role
    return None

def get_product_by_id(product_id):
    # Try to get the product from the database
    product = Product.query.get(product_id)
    
    if product:
        # Convert SQLAlchemy model to dictionary
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'image': product.image,
            'category_id': product.category_id,
            'category': {
                'id': product.category.id,
                'name': product.category.name
            } if product.category else None
        }
    return None

def get_category_by_id(category_id):
    for category in categories:
        if category['id'] == category_id:
            return category
    return None

def get_order_by_id(order_id):
    for order in orders:
        if order['id'] == order_id:
            return order
    return None

def calculate_stats():
    stats = {}
    stats['total_orders'] = len(orders)
    stats['total_revenue'] = sum(order['total_amount'] for order in orders)
    stats['total_customers'] = sum(1 for user in users if not user['is_admin'])
    stats['total_products'] = len(product_list)
    return stats

def get_recent_orders(limit=5):
    recent = sorted(orders, key=lambda x: x['order_date'], reverse=True)[:limit]
    for order in recent:
        customer = get_user_by_id(order['customer_id'])
        order['customer_name'] = f"{customer['first_name']} {customer['last_name']}"
        order['date'] = order['order_date']
    return recent

# Admin panel routes
@app.route('/admin/products')
def admin_products():
    return render_template('admin/products.html', products=product_list, categories=categories)

@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_product_new():
    if request.method == 'POST':
        # Handle form submission (in a real app)
        flash('Product added successfully', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=None, categories=categories)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    product = get_product_by_id(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        # Handle form submission (in a real app)
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=product, categories=categories)

@app.route('/admin/orders')
def admin_orders():
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>')
def admin_order_detail(order_id):
    order = get_order_by_id(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('admin_orders'))
    
    order['customer'] = get_user_by_id(order['customer_id'])
    
    return render_template('admin/order_detail.html', order=order, order_items=[])

@app.route('/admin/users')
def admin_users():
    # Get the current user information from session
    current_user = get_user_by_id(session['user_id']) if 'user_id' in session else None
    return render_template('admin/users.html', users=users)

@app.route('/admin/settings')
def admin_settings():
    settings = {
        'site_name': 'Mango Delight',
        'tagline': 'The Best Mangoes from India',
        'primary_color': '#198754',
        'footer_text': '© 2023 Mango Delight. All rights reserved.',
    }
    
    return render_template('admin/settings.html', 
                          settings=settings, 
                          backups=[],
                          shipping_options=[])

@app.route('/admin/categories')
def admin_categories():
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/reviews')
def admin_reviews():
    return render_template('admin/reviews.html', reviews=[])

# Front-end routes
@app.route('/products')
def products():
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')
    
    # Filter products (in a real app, this would use database queries)
    filtered_products = product_list
    
    if category_id:
        filtered_products = [p for p in filtered_products if p['category_id'] == category_id]
    
    if search_query:
        filtered_products = [p for p in filtered_products if search_query.lower() in p['name'].lower() or search_query.lower() in p['description'].lower()]
    
    # Sort products
    if sort_by == 'price_low':
        filtered_products = sorted(filtered_products, key=lambda x: x['price'])
    elif sort_by == 'price_high':
        filtered_products = sorted(filtered_products, key=lambda x: x['price'], reverse=True)
    else:  # Default: sort by name
        filtered_products = sorted(filtered_products, key=lambda x: x['name'])
    
    # Add a helper function to get category name by ID
    def get_category_name(category_id):
        category = get_category_by_id(category_id)
        return category['name'] if category else 'Unknown'
    
    return render_template('products.html', 
                          products=filtered_products,
                          categories=categories,
                          current_category=category_id,
                          search_query=search_query,
                          sort_by=sort_by,
                          get_category_name=get_category_name)  # Pass the helper function

@app.route('/')
def home():
    return render_template('index.html', products=product_list[:4])  # Show just first 4 products

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Get product by ID
    product = get_product_by_id(product_id)
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products'))
    
    # Add category information to product
    category = get_category_by_id(product['category_id'])
    if category:
        product['category'] = {
            'id': category['id'],
            'name': category['name']
        }
    
    # Get related products (same category but not the same product)
    related_products = [p for p in product_list if p['category_id'] == product['category_id'] and p['id'] != product_id][:4]
    
    # Add a helper function to get category name by ID for the template
    def get_category_name(category_id):
        category = get_category_by_id(category_id)
        return category['name'] if category else 'Unknown'
    
    return render_template('product_detail.html', 
                          product=product,
                          related_products=related_products,
                          reviews=[],
                          get_category_name=get_category_name)  # Pass the helper function

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # In a real application, you would save the form data to database
        # or send an email
        name = request.form.get('name')
        flash(f'Thank you {name} for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/cart')
def cart():
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please login to view your cart.', 'warning')
            return redirect(url_for('login', next=url_for('cart')))
        
        # Get user's cart
        cart_items = []
        total = 0
        
        # Check if user has cart items in session
        if 'cart' in session:
            # Get cart items from session
            cart_data = session['cart']
            print(f"Cart data: {cart_data}")
            
            # Loop through cart items
            for item_id, item_data in cart_data.items():
                # Get product details
                try:
                    product_id = int(item_id)
                    product = get_product_by_id(product_id)
                    print(f"Retrieved product for ID {product_id}: {product}")
                    
                    if product:
                        # Calculate item total
                        item_total = product['price'] * item_data['quantity']
                        total += item_total
                        
                        # Add item to cart items list
                        cart_items.append({
                            'product': product,
                            'quantity': item_data['quantity'],
                            'total': item_total
                        })
                    else:
                        print(f"Product with ID {product_id} not found")
                except Exception as e:
                    print(f"Error processing cart item {item_id}: {str(e)}")
        else:
            print("No cart in session")
        
        # Get recommended products for "You May Also Like" section
        products = Product.query.filter(Product.stock > 0).order_by(db.func.random()).limit(4).all()
        recommended_products = []
        
        for product in products:
            recommended_products.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'stock': product.stock,
                'image': product.image,
                'category_id': product.category_id
            })
        
        return render_template('cart.html', 
                              cart_items=cart_items, 
                              total=total,
                              products=recommended_products)
    except Exception as e:
        print(f"Error in cart route: {str(e)}")
        flash('An error occurred while loading your cart. Please try again.', 'danger')
        return redirect(url_for('home'))

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please login to add products to cart.', 'warning')
            return redirect(url_for('login', next=url_for('product_detail', product_id=product_id)))
        
        # Get product details
        product = get_product_by_id(product_id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))
        
        # Get quantity from form
        quantity = int(request.form.get('quantity', 1))
        
        # Validate quantity
        if quantity <= 0:
            quantity = 1
        
        # Check if product is in stock
        if product['stock'] < quantity:
            flash(f'Sorry, only {product["stock"]} items available in stock.', 'warning')
            quantity = product['stock']
        
        # Initialize cart in session if not exists
        if 'cart' not in session:
            session['cart'] = {}
        
        # Add product to cart
        cart = session['cart']
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            # Update quantity if product already in cart
            cart[product_id_str]['quantity'] += quantity
        else:
            # Add new product to cart
            cart[product_id_str] = {
                'quantity': quantity
            }
        
        # Save cart to session
        session['cart'] = cart
        session.modified = True
        
        flash(f'Added {quantity} {product["name"]} to your cart!', 'success')
        return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        flash('An error occurred while adding item to cart. Please try again.', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))

# Update products.html add to cart buttons
@app.route('/quick-add-to-cart/<int:product_id>', methods=['POST'])
def quick_add_to_cart(product_id):
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please login to add products to cart.', 'warning')
            return redirect(url_for('login'))
        
        # Get product details
        product = get_product_by_id(product_id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))
        
        # Initialize cart in session if not exists
        if 'cart' not in session:
            session['cart'] = {}
        
        # Add product to cart
        cart = session['cart']
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            # Update quantity if product already in cart
            cart[product_id_str]['quantity'] += 1
        else:
            # Add new product to cart
            cart[product_id_str] = {
                'quantity': 1
            }
        
        # Save cart to session
        session['cart'] = cart
        session.modified = True
        
        flash(f'Added {product["name"]} to your cart!', 'success')
        
        # Redirect to referring page or products page if no referrer
        if request.referrer:
            return redirect(request.referrer)
        else:
            return redirect(url_for('products'))
    except Exception as e:
        print(f"Error in quick_add_to_cart: {str(e)}")
        flash('An error occurred while adding item to cart. Please try again.', 'danger')
        return redirect(url_for('products'))

@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to manage your cart.', 'warning')
        return redirect(url_for('login'))
    
    # Check if cart exists in session
    if 'cart' not in session:
        return redirect(url_for('cart'))
    
    # Get cart from session
    cart = session['cart']
    product_id_str = str(product_id)
    
    # Remove product from cart if exists
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        flash('Product removed from cart.', 'success')
    
    return redirect(url_for('cart'))

@app.route('/update-cart', methods=['POST'])
def update_cart():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to manage your cart.', 'warning')
        return redirect(url_for('login'))
    
    # Check if cart exists in session
    if 'cart' not in session:
        return redirect(url_for('cart'))
    
    # Get cart from session
    cart = session['cart']
    
    # Update quantities
    for product_id, quantity in request.form.items():
        if product_id.startswith('quantity_'):
            product_id_str = product_id.replace('quantity_', '')
            if product_id_str in cart:
                try:
                    new_quantity = int(quantity)
                    if new_quantity > 0:
                        cart[product_id_str]['quantity'] = new_quantity
                    elif new_quantity <= 0:
                        del cart[product_id_str]
                except ValueError:
                    pass
    
    # Save updated cart to session
    session['cart'] = cart
    flash('Cart updated successfully.', 'success')
    
    return redirect(url_for('cart'))

# Booking routes
@app.route('/book-mangoes', methods=['GET', 'POST'])
def book_mangoes():
    try:
        if 'user_id' not in session:
            flash('Please login to book mangoes.', 'warning')
            return redirect(url_for('login', next=url_for('book_mangoes')))
        
        if request.method == 'POST':
            # Get form data
            product_id = request.form.get('product_id', type=int)
            quantity = request.form.get('quantity', type=int)
            delivery_date = request.form.get('delivery_date')
            shipping_address = request.form.get('shipping_address')
            phone = request.form.get('phone')
            notes = request.form.get('notes', '')
            
            print(f"Form data: product_id={product_id}, quantity={quantity}, delivery_date={delivery_date}")
            
            # Validate required fields
            if not product_id:
                flash('Please select a mango variety.', 'danger')
                return redirect(url_for('book_mangoes'))
                
            if not quantity or quantity <= 0 or quantity > 10:
                flash('Please enter a valid quantity between 1 and 10 dozens.', 'danger')
                return redirect(url_for('book_mangoes'))
                
            if not delivery_date:
                flash('Please select a delivery date.', 'danger')
                return redirect(url_for('book_mangoes'))
                
            if not shipping_address:
                flash('Please enter your shipping address.', 'danger')
                return redirect(url_for('book_mangoes'))
                
            if not phone or len(phone) != 10 or not phone.isdigit():
                flash('Please enter a valid 10-digit phone number.', 'danger')
                return redirect(url_for('book_mangoes'))
            
            # Convert delivery_date string to date object
            try:
                delivery_date_obj = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                
                # Check if delivery date is at least 3 days from today
                min_date = datetime.now().date() + timedelta(days=3)
                if delivery_date_obj < min_date:
                    flash('Delivery date must be at least 3 days from today.', 'danger')
                    return redirect(url_for('book_mangoes'))
                    
            except ValueError:
                flash('Invalid delivery date format.', 'danger')
                return redirect(url_for('book_mangoes'))
            
            # Get product details
            product = Product.query.get(product_id)
            if not product:
                flash('Selected product does not exist.', 'danger')
                return redirect(url_for('book_mangoes'))
            
            # Calculate total amount
            total_amount = product.price * quantity
            
            # Create new booking
            new_booking = Booking(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity,
                delivery_date=delivery_date_obj,
                notes=notes,
                total_amount=total_amount,
                shipping_address=shipping_address,
                phone=phone,
                status='pending',
                payment_status='pending',
                booking_date=datetime.now()
            )
            
            try:
                db.session.add(new_booking)
                db.session.commit()
                
                # Get the newly created booking ID
                booking_id = new_booking.id
                
                flash('Your mango booking has been placed successfully! You will receive a confirmation soon.', 'success')
                return redirect(url_for('booking_detail', booking_id=booking_id))
            except Exception as e:
                db.session.rollback()
                print(f"Error creating booking: {str(e)}")
                flash(f'An error occurred while placing your booking. Please try again.', 'danger')
                return redirect(url_for('book_mangoes'))
        
        # GET request - display booking form
        products = Product.query.filter(Product.stock > 0).all()
        
        # If no products found in database, use mock data
        if not products:
            products = product_list
            
        return render_template('book_mangoes.html', products=products)
    
    except Exception as e:
        print(f"Error in book_mangoes: {str(e)}")
        flash('An unexpected error occurred. Please try again later.', 'danger')
        return redirect(url_for('home'))

@app.route('/my-bookings')
def my_bookings():
    try:
        if 'user_id' not in session:
            flash('Please login to view your bookings.', 'warning')
            return redirect(url_for('login', next=url_for('my_bookings')))
        
        # Get user's bookings
        user_id = session['user_id']
        
        # Get bookings sorted by date (newest first)
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
        
        # Group bookings by status
        pending_bookings = []
        active_bookings = []  # confirmed, but not yet delivered
        completed_bookings = []  # delivered or cancelled
        
        for booking in bookings:
            if booking.status == 'pending':
                pending_bookings.append(booking)
            elif booking.status == 'confirmed':
                active_bookings.append(booking)
            else:
                completed_bookings.append(booking)
        
        return render_template('my_bookings.html', 
                             bookings=bookings,
                             pending_bookings=pending_bookings,
                             active_bookings=active_bookings,
                             completed_bookings=completed_bookings)
                             
    except Exception as e:
        print(f"Error in my_bookings: {str(e)}")
        flash('An error occurred while retrieving your bookings.', 'danger')
        return redirect(url_for('home'))

@app.route('/booking/<int:booking_id>')
def booking_detail(booking_id):
    try:
        if 'user_id' not in session:
            flash('Please login to view booking details.', 'warning')
            return redirect(url_for('login', next=url_for('booking_detail', booking_id=booking_id)))
        
        user_id = session['user_id']
        user_role = get_user_role(user_id)
        
        # Get booking details
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if booking belongs to current user or user is admin
        if booking.user_id != user_id and user_role != 'admin':
            flash('You are not authorized to view this booking.', 'danger')
            return redirect(url_for('my_bookings'))
        
        # Get product details for the booking
        product = Product.query.get(booking.product_id)
        
        # Check if delivery date has passed
        is_past_delivery = booking.delivery_date < datetime.now().date()
        
        # Check if cancellation is allowed (only if status is pending or confirmed AND delivery date is more than 24 hours away)
        can_cancel = False
        if booking.status in ['pending', 'confirmed']:
            time_until_delivery = (datetime.combine(booking.delivery_date, datetime.min.time()) - datetime.now()).total_seconds() / 3600
            can_cancel = time_until_delivery > 24
        
        return render_template('booking_detail.html', 
                             booking=booking, 
                             product=product,
                             is_past_delivery=is_past_delivery,
                             can_cancel=can_cancel)
                             
    except Exception as e:
        print(f"Error in booking_detail: {str(e)}")
        flash('An error occurred while retrieving booking details.', 'danger')
        return redirect(url_for('my_bookings'))

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    try:
        if 'user_id' not in session:
            flash('Please login to cancel bookings.', 'warning')
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        user_role = get_user_role(user_id)
        
        # Get booking details
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if booking belongs to current user or user is admin
        if booking.user_id != user_id and user_role != 'admin':
            flash('You are not authorized to cancel this booking.', 'danger')
            return redirect(url_for('my_bookings'))
        
        # Check if booking can be cancelled
        if booking.status in ['delivered', 'cancelled']:
            flash('This booking cannot be cancelled as it is already delivered or cancelled.', 'danger')
            return redirect(url_for('booking_detail', booking_id=booking_id))
        
        # Check if cancellation is allowed (delivery date is more than 24 hours away)
        time_until_delivery = (datetime.combine(booking.delivery_date, datetime.min.time()) - datetime.now()).total_seconds() / 3600
        if time_until_delivery <= 24 and user_role != 'admin':
            flash('Bookings can only be cancelled at least 24 hours before the delivery date.', 'danger')
            return redirect(url_for('booking_detail', booking_id=booking_id))
        
        # Update booking status
        booking.status = 'cancelled'
        
        try:
            db.session.commit()
            flash('Your booking has been cancelled successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error cancelling booking: {str(e)}")
            flash('An error occurred while cancelling your booking. Please try again.', 'danger')
        
        return redirect(url_for('booking_detail', booking_id=booking_id))
        
    except Exception as e:
        print(f"Error in cancel_booking: {str(e)}")
        flash('An error occurred while processing your request.', 'danger')
        return redirect(url_for('my_bookings'))

# Admin booking routes
@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    try:
        # Get filter parameters from query string
        status_filter = request.args.get('status', 'all')
        date_filter = request.args.get('date', 'all')
        sort_by = request.args.get('sort', 'date_desc')
        
        # Base query
        query = Booking.query
        
        # Apply status filter
        if status_filter != 'all':
            query = query.filter(Booking.status == status_filter)
        
        # Apply date filter
        today = datetime.now().date()
        if date_filter == 'today':
            query = query.filter(Booking.delivery_date == today)
        elif date_filter == 'upcoming':
            query = query.filter(Booking.delivery_date > today)
        elif date_filter == 'past':
            query = query.filter(Booking.delivery_date < today)
        
        # Apply sorting
        if sort_by == 'date_asc':
            query = query.order_by(Booking.delivery_date.asc())
        elif sort_by == 'date_desc':
            query = query.order_by(Booking.delivery_date.desc())
        elif sort_by == 'booking_asc':
            query = query.order_by(Booking.booking_date.asc())
        else:  # booking_desc
            query = query.order_by(Booking.booking_date.desc())
        
        # Execute query
        bookings = query.all()
        
        # Get statistics
        stats = {
            'total': Booking.query.count(),
            'pending': Booking.query.filter_by(status='pending').count(),
            'confirmed': Booking.query.filter_by(status='confirmed').count(),
            'delivered': Booking.query.filter_by(status='delivered').count(),
            'cancelled': Booking.query.filter_by(status='cancelled').count(),
            'today_deliveries': Booking.query.filter(
                Booking.delivery_date == today,
                Booking.status.in_(['pending', 'confirmed'])
            ).count(),
            'upcoming_deliveries': Booking.query.filter(
                Booking.delivery_date > today,
                Booking.status.in_(['pending', 'confirmed'])
            ).count()
        }
        
        return render_template(
            'admin/bookings.html', 
            bookings=bookings,
            status_filter=status_filter,
            date_filter=date_filter,
            sort_by=sort_by,
            stats=stats
        )
    except Exception as e:
        print(f"Error in admin_bookings: {str(e)}")
        flash('An error occurred while retrieving booking data.', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/<int:booking_id>')
@admin_required
def admin_booking_detail(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Get user details
        user = User.query.get(booking.user_id)
        
        # Get product details
        product = Product.query.get(booking.product_id)
        
        # Calculate if delivery date has passed
        is_past_delivery = booking.delivery_date < datetime.now().date()
        
        return render_template(
            'admin/booking_detail.html', 
            booking=booking,
            user=user,
            product=product,
            is_past_delivery=is_past_delivery
        )
    except Exception as e:
        print(f"Error in admin_booking_detail: {str(e)}")
        flash('An error occurred while retrieving booking details.', 'danger')
        return redirect(url_for('admin_bookings'))

@app.route('/admin/booking/update-status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        status = request.form.get('status')
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'delivered', 'cancelled']
        if status not in valid_statuses:
            flash('Invalid booking status.', 'danger')
            return redirect(url_for('admin_booking_detail', booking_id=booking_id))
        
        # Update status
        booking.status = status
        
        # If status is delivered, update payment_status to paid
        if status == 'delivered':
            booking.payment_status = 'paid'
        
        try:
            db.session.commit()
            flash('Booking status updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error updating booking status: {str(e)}")
            flash('An error occurred while updating the booking status.', 'danger')
        
        return redirect(url_for('admin_booking_detail', booking_id=booking_id))
    except Exception as e:
        print(f"Error in update_booking_status: {str(e)}")
        flash('An error occurred while processing your request.', 'danger')
        return redirect(url_for('admin_bookings'))

if __name__ == '__main__':
    # Use PORT environment variable if available (for production)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)