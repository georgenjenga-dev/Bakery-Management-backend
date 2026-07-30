from app.extensions import db
from app.models.models import Admin


def get_all_admins():
    admins = Admin.query.all()
    return [admin.to_dict() for admin in admins]


def create_admin(data):
    existing_email = Admin.query.filter_by(
        email=data["email"]
    ).first()

    if existing_email:
        return {
            "success": False,
            "message": "Email already exists."
        }

    existing_username = Admin.query.filter_by(
        username=data["username"]
    ).first()

    if existing_username:
        return {
            "success": False,
            "message": "Username already exists."
        }

    admin = Admin(
        username=data["username"],
        email=data["email"],
        role="admin",          # Always create as a normal admin
        is_active=True
    )

    admin.set_password(data["password"])

    db.session.add(admin)
    db.session.commit()

    return {
        "success": True,
        "message": "Admin created successfully.",
        "admin": admin.to_dict()
    }


def deactivate_admin(admin_id):
    admin = db.session.get(Admin, admin_id)

    if not admin:
        return {
            "success": False,
            "message": "Admin not found."
        }

    if admin.role == "super_admin":
        return {
            "success": False,
            "message": "Super Admin cannot be deactivated."
        }

    admin.is_active = False

    db.session.commit()

    return {
        "success": True,
        "message": "Admin deactivated successfully."
    }


def activate_admin(admin_id):
    admin = db.session.get(Admin, admin_id)

    if not admin:
        return {
            "success": False,
            "message": "Admin not found."
        }

    admin.is_active = True

    db.session.commit()

    return {
        "success": True,
        "message": "Admin activated successfully."
    }


def reset_password(admin_id, new_password):
    admin = db.session.get(Admin, admin_id)

    if not admin:
        return {
            "success": False,
            "message": "Admin not found."
        }

    admin.set_password(new_password)

    db.session.commit()

    return {
        "success": True,
        "message": "Password reset successfully."
    }