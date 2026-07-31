import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import or_

from app import create_app
from app.extensions import db
from app.models.models import Admin
import getpass


def create_admin():
    app = create_app()
    with app.app_context():
        if len(sys.argv) >= 4:
            email = sys.argv[1]
            username = sys.argv[2]
            password = sys.argv[3]
        else:
            email = input("Enter admin email: ")
            username = input("Enter admin username: ")
            password = getpass.getpass("Enter admin password: ")

        existing_admin = Admin.query.filter(
            or_(Admin.email == email, Admin.username == username)
        ).first()
        if existing_admin:
            print(
                f"Admin already exists with username '{existing_admin.username}' and email '{existing_admin.email}'."
            )
            return

        admin = Admin(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print(f"Admin {username} created successfully.")


if __name__ == '__main__':
    create_admin()