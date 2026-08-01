# Sweet Delicacy Bakery — Backend

##  Project Overview

The **Sweet Delicacy Bakery Management System Backend** is a Flask-based backend application that provides the server-side functionality required by the bakery management system.

It manages bakery products, customer orders, inventory-related information, and administrative operations through a relational database.

The backend works together with the React frontend to provide customers with an online platform for browsing bakery products and placing orders, while administrators can securely manage products, inventory, and customer orders.

##  Backend Features

### Customer Operations

The backend supports functionality required for customers to:

* Browse bakery products
* Search for products
* View product details
* Add products to a shopping cart
* Place orders
* Proceed to payment

These customer features form part of the overall bakery solution described in the project documentation.

### Administrator Operations

The backend supports administrative functionality including:

* Secure administrator login
* Adding new bakery products
* Editing product information
* Deleting products
* Uploading product images
* Viewing customer orders
* Updating order status
* Monitoring inventory

## 🛠️ Technologies Used

* **Python** — Backend programming language
* **Flask** — Web application framework
* **Flask-SQLAlchemy** — Database ORM
* **SQLite** — Relational database
* **REST API** — Communication with the React frontend
* **Render** — Backend deployment platform

The project documentation specifically identifies Flask-SQLAlchemy and SQLite as the backend/database technologies.

##  Backend Structure

A typical Flask backend structure can be organized as:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── controllers/
│   └── ...
├── instance/
│   └── database.db
├── config.py
├── run.py
├── requirements.txt
├── .env
└── README.md
```

> The exact structure should match the actual backend repository.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/georgenjenga-dev/Bakery-Management-backend.git
```

### 2. Create a Virtual Environment

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```


### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file does not yet exist, the project should include the Flask and Flask-SQLAlchemy dependencies required by the implementation.

### 4. Configure Environment Variables

Create a `.env` file for environment-specific configuration.

Example:

```env
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///bakery.db
```

> Use the actual configuration variables defined by your backend code. Do not commit sensitive `.env` values to GitHub.

### 5. Initialize the Database

The backend uses **SQLite** as its database technology.

Run the database initialization or migration command required by your implementation.

For example, if the project uses Flask-Migrate:

```bash
flask db upgrade
```

> Use the database command actually implemented in the project.

### 6. Run the Backend

Depending on how the Flask application is configured:

```bash
flask run
```

or:

```bash
python run.py
```

The backend will normally be available at:

```text
http://127.0.0.1:5000
```

##  API Responsibilities

The backend provides the server-side functionality required by the frontend.

Its responsibilities include:

### Products

* Retrieve bakery products
* Search bakery products
* Retrieve product details
* Add products
* Update product information
* Delete products
* Handle product images

### Orders

* Create customer orders
* Retrieve customer orders
* Allow administrators to view orders
* Update order status

### Inventory

* Store product-related inventory information
* Allow administrators to monitor inventory
* Support inventory management operations

### Authentication

* Provide secure administrator authentication
* Protect administrator functionality from unauthorized access

The project documentation identifies secure administrator login, product management, order management, and inventory monitoring as administrator functionality.

## Database

The backend uses:

**Database:** SQLite
**ORM:** Flask-SQLAlchemy

The relational database is responsible for storing and managing the application's data efficiently, supporting product, order, and operational management.

##  Security

The backend should:

* Keep secret keys in environment variables
* Protect administrator routes
* Validate incoming data
* Avoid exposing sensitive configuration
* Prevent `.env` files from being committed to Git
* Restrict administrative operations to authorized users

## Deployment

The backend is intended to be deployed independently from the React frontend.

**Deployment platform:** Render

The project document provides the following backend deployment:

**Sweet Delicacy Bakery Backend:**
https://bakery-management-backend-1.onrender.com/

The project documentation identifies Render as the backend deployment platform.

## Frontend Integration

The backend communicates with the React frontend through API requests.

The frontend uses the backend to access functionality related to:

```text
Products
    ↓
Product Details
    ↓
Shopping Cart
    ↓
Orders
    ↓
Payment
```

Administrators use the backend to manage:

```text
Admin Login
    ↓
Product Management
    ↓
Inventory Monitoring
    ↓
Customer Orders
    ↓
Order Status Updates
```

## Project Objective

The backend helps transform traditional manual bakery operations into an organized online management system.

The solution is designed to improve:

* Order processing
* Product management
* Inventory management
* Customer service
* Overall bakery operational efficiency

##  Contributors

* Baker George
* Baker Elias
* Baker Joshua
* Baker Kelvin

## License

This project was developed as a bakery management system project. Add the appropriate license here if the project is released publicly.
