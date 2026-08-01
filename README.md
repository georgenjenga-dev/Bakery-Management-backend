# Sweet Delicacy Bakery — Frontend

## Project Overview

The **Sweet Delicacy Bakery Management System** is a responsive web application that provides customers with an easy and convenient way to explore bakery products and place orders online.

The frontend is responsible for providing the user interface through which customers can browse products, search for products, view product details, add products to a shopping cart, place orders, and proceed to payment.

The application also provides interfaces for administrators to manage bakery products and customer orders.

## Features

### Customer Features

* Browse available bakery products
* Search for bakery products
* View product details
* Add products to a shopping cart
* Manage products in the shopping cart
* Place customer orders
* Proceed to payment
* Use a responsive interface across different screen sizes

### Administrator Features

The frontend provides interfaces that support administrative operations such as:

* Secure administrator login
* Add new bakery products
* Edit product information
* Delete products
* Upload product images
* View customer orders
* Update order status
* Monitor inventory

##  Technologies Used

* **React** — Frontend JavaScript library
* **Tailwind CSS** — Styling and responsive UI
* **JavaScript** — Application logic
* **REST API** — Communication with the Flask backend
* **Vercel** — Frontend deployment platform

## Frontend Structure

A typical project structure is:

```text
frontend/
├── public/
├── src/
│   ├── components/
│   ├── pages/
│   ├── assets/
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

> The exact folder structure may differ depending on the implementation of the project.

##  Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/georgenjenga-dev/Bakery-management-frontend.git
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Backend API

The frontend communicates with the Flask backend to retrieve products, manage orders, and perform other application operations.

If the project uses an environment variable for the backend URL, create an environment file such as:

```text
.env
```

and configure the backend API URL according to your project setup.

Example:

```env
VITE_API_URL=https://bakery-management-backend-1.onrender.com
```

> Use the actual variable name and backend URL configured in your project.

### 4. Start the Development Server

```bash
npm run dev
```

The application will normally be available through the local development URL displayed in your terminal.

## Backend Integration

The frontend communicates with the Flask backend to support operations such as:

* Retrieving bakery products
* Searching products
* Viewing product information
* Managing shopping cart information
* Creating customer orders
* Processing order-related operations
* Retrieving customer orders
* Supporting administrator product management
* Updating order status

The backend uses **Flask-SQLAlchemy** with **SQLite** as the database technology.

## Deployment

The frontend is intended to be deployed separately from the backend.

### Frontend Deployment

**Platform:** Render

The project documentation provides the following deployed frontend:

**Sweet Delicacy Bakery Frontend:**
https://bakery-management-frontend-41cl.onrender.com/

##  Project Purpose

The frontend helps replace manual bakery ordering processes with an online platform where customers can conveniently browse products and place orders. This addresses challenges such as misplaced orders, stock inconsistencies, and delayed customer service.

##  Contributors

* Baker George
* Baker Elias
* Baker Joshua
* Baker Kelvin

##  License

This project was developed as a bakery management system project. Add the appropriate license here if the project is released publicly.
