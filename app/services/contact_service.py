from app.extensions import db
from app.models.models import ContactMessage


def create_message(data):

    message = ContactMessage(
        full_name=data["full_name"],
        email=data["email"],
        subject=data["subject"],
        message=data["message"]
    )

    db.session.add(message)
    db.session.commit()

    return message


def get_messages():

    messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).all()

    return [m.to_dict() for m in messages]


def get_message(message_id):

    return db.session.get(
        ContactMessage,
        message_id
    )


def delete_message(message):

    db.session.delete(message)
    db.session.commit()