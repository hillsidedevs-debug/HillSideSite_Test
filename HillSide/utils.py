from functools import wraps
from flask import abort, url_for
from flask_login import current_user
from HillSide.extensions import mail
from flask_mail import Message
from .config import Config
import uuid
import os

from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
                                    
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)

    msg = Message(
        subject="Password Reset Request",
        sender="no-reply@hillside.com",
        recipients=[user.email]
    )
    msg.body = f"""Hello,

To reset your password, click the link below:

{reset_url}

If you did not request this, simply ignore this message.
"""

    mail.send(msg)

def send_verification_email(user):
    token = serializer.dumps(user.email, salt="email-verify")

    link = url_for('auth.verify_email', token=token, _external=True)

    msg = Message(
        subject="Verify Your Email",
        recipients=[user.email],
        body=f"Click the link to verify your email: {link}"
    )

    mail.send(msg)

def generate_secure_filename(prefix, extension):
    return f"{prefix}_{uuid.uuid4().hex}.{extension}"

import magic # pip install python-magic

def is_valid_file(file_storage, expected_mime_group):
    header = file_storage.read(2048)
    file_storage.seek(0)
    
    mime = magic.from_buffer(header, mime=True)
    
    if expected_mime_group == 'image':
        return mime in ['image/jpeg', 'image/png']
    if expected_mime_group == 'pdf':
        return mime == 'application/pdf'
    # Inside is_valid_file(file_storage, expected_mime_group)
    if expected_mime_group == 'video':
        return mime in ['video/mp4', 'video/webm', 'video/quicktime', 'video/x-matroska']
    return False

