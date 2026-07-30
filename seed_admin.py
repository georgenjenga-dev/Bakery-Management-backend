import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.models import Admin
import getpass

def create_admin():
    app = create_app()
    with app.app_context():
        email = input("Enter admin email: ")
        if Admin.query.filter_by(email=email).first():
            print("Admin already exists.")
            return
        username = input("Enter admin username: ")
        password = getpass.getpass("Enter admin password: ")
        admin = Admin(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin {username} created successfully.")

if __name__ == '__main__':
    create_admin()