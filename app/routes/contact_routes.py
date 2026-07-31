from flask import Blueprint, request

from app.services.contact_service import (
    create_message,
    get_messages,
    get_message,
    delete_message,
)

from app.utils.helpers import (
    success_response,
    error_response,
    admin_required,
)

from app.utils.validators import (
    validate_contact,
)

contact_bp = Blueprint(
    "contact",
    __name__,
    url_prefix="/contact",
)


@contact_bp.post("/")
def send_message():

    data = request.get_json(silent=True)

    if data is None:
        return error_response(
            "Invalid JSON body"
        )

    valid, error = validate_contact(data)

    if not valid:
        return error_response(error)

    message = create_message(data)

    return success_response(
        message.to_dict(),
        "Message sent successfully",
        201,
    )


@contact_bp.get("/")
@admin_required()
def all_messages():

    return success_response(
        get_messages()
    )


@contact_bp.get("/<int:message_id>")
@admin_required()
def one_message(message_id):

    message = get_message(message_id)

    if not message:
        return error_response(
            "Message not found",
            404,
        )

    return success_response(
        message.to_dict()
    )


@contact_bp.delete("/<int:message_id>")
@admin_required()
def remove_message(message_id):

    message = get_message(message_id)

    if not message:
        return error_response(
            "Message not found",
            404,
        )

    delete_message(message)

    return success_response(
        message="Message deleted successfully"
    )