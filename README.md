# Mango Delight

A mango e-commerce website built with Flask that allows users to browse and book mangoes in advance.

## Features

- User authentication (register, login, logout)
- Mango product showcase with details
- Mango booking system for delivery on specific dates
- Admin panel for managing products, bookings, and users
- Responsive design using Bootstrap

## Deployment to Render

This application is configured for deployment on Render.com.

### Steps to deploy:

1. Create a new account on [Render](https://render.com/) if you don't have one
2. Connect your GitHub repository to Render
3. Create a new Web Service and select your repository
4. Use the following settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add the following environment variables:
   - `SECRET_KEY`: [Generate a random secret key]
   - `DATABASE_URL`: [Your database connection string]
   - `PYTHON_VERSION`: 3.9.12

## Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pandeymango.git
   cd pandeymango
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   flask run
   ```

5. Visit `http://localhost:5000` in your browser.

## Database Setup

The application uses MySQL by default. Update the database connection string in app.py or set it as an environment variable.

## Credits

Developed by: Somil Pandey

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite

## Project Structure

```
mango-ecommerce/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
├── app.py
├── database.py
├── models.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```
   python database.py
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`

## Features

- Product catalog with different mango varieties
- User registration and login
- Shopping cart functionality
- Order placement and tracking
- Admin panel for inventory management
