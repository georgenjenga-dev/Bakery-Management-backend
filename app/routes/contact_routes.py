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
    """
    POST /contact
    Submit a contact message
    ---
    tags:
      - Contact
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - full_name
            - email
            - subject
            - message
          properties:
            full_name:
              type: string
              example: "Jane Wanjiru"
            email:
              type: string
              example: "jane@example.com"
            subject:
              type: string
              example: "Inquiry about custom cake"
            message:
              type: string
              example: "I would like to order a custom cake for my birthday."
    responses:
      201:
        description: Message sent successfully
      400:
        description: Validation error
    """

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
    """
    GET /contact
    Get all contact messages (Admin only)
    ---
    tags:
      - Contact
    security:
      - admin: []
    responses:
      200:
        description: List of all contact messages
      401:
        description: Admin authentication required
    """

    return success_response(
        get_messages()
    )


@contact_bp.get("/<int:message_id>")
@admin_required()
def one_message(message_id):
    """
    GET /contact/<message_id>
    Get a single contact message
    ---
    tags:
      - Contact
    security:
      - admin: []
    parameters:
      - in: path
        name: message_id
        required: true
        type: integer
        description: The message ID
    responses:
      200:
        description: Message details
      401:
        description: Admin authentication required
      404:
        description: Message not found
    """

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
    """
    DELETE /contact/<message_id>
    Delete a contact message (Admin only)
    ---
    tags:
      - Contact
    security:
      - admin: []
    parameters:
      - in: path
        name: message_id
        required: true
        type: integer
        description: The message ID
    responses:
      200:
        description: Message deleted successfully
      401:
        description: Admin authentication required
      404:
        description: Message not found
    """

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